"""
Macro Recording and Playback Module
Enables recording, editing, and replaying browser automation workflows.
"""

import json
import time
import logging
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path


@dataclass
class MacroAction:
    """
    Represents a single action in a macro workflow.
    """
    action: str  # e.g., "click", "send_keys", "navigate", "wait", "assert_text", "screenshot"
    selector: str = ""  # xpath or css selector
    selector_type: str = "xpath"  # "xpath" or "css"
    value: str = ""  # value or template (e.g., "{invoice_number}")
    timeout: float = 10.0
    retries: int = 3
    description: str = ""  # Human-readable description
    meta: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'MacroAction':
        """Create MacroAction from dictionary."""
        # Handle missing 'meta' field for backward compatibility
        if 'meta' not in data:
            data['meta'] = {}
        return MacroAction(**data)


class MacroRecorder:
    """
    Records browser automation actions into replayable macros.
    """
    
    def __init__(self):
        """Initialize the macro recorder."""
        self.actions: List[MacroAction] = []
        self.recording = False
        self.macro_name = ""
        self.start_time = None
        
    def start(self, macro_name: str = "unnamed_macro"):
        """
        Start recording a new macro.
        
        Args:
            macro_name (str): Name for the macro being recorded
        """
        self.actions = []
        self.recording = True
        self.macro_name = macro_name
        self.start_time = time.time()
        logging.info(f"🔴 Started recording macro: {macro_name}")
    
    def stop(self):
        """Stop recording the current macro."""
        self.recording = False
        duration = time.time() - self.start_time if self.start_time else 0
        logging.info(f"⏹️ Stopped recording macro: {self.macro_name} ({len(self.actions)} actions, {duration:.1f}s)")
        return len(self.actions)
    
    def record_action(self, action: MacroAction):
        """
        Record a single action.
        
        Args:
            action (MacroAction): Action to record
        """
        if self.recording:
            self.actions.append(action)
            logging.debug(f"📝 Recorded action: {action.action} - {action.description}")
    
    def save(self, path: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Save recorded macro to JSON file.
        
        Args:
            path (str): File path to save macro
            metadata (dict, optional): Additional metadata to include
        """
        payload = {
            "version": 1,
            "name": self.macro_name,
            "created_at": datetime.now().isoformat(),
            "duration": time.time() - self.start_time if self.start_time else 0,
            "action_count": len(self.actions),
            "metadata": metadata or {},
            "actions": [action.to_dict() for action in self.actions]
        }
        
        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        
        logging.info(f"💾 Saved macro to: {path}")
    
    def load(self, path: str) -> bool:
        """
        Load macro from JSON file.
        
        Args:
            path (str): File path to load macro from
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            
            self.macro_name = payload.get("name", "loaded_macro")
            self.actions = [MacroAction.from_dict(a) for a in payload.get("actions", [])]
            
            logging.info(f"📂 Loaded macro: {self.macro_name} ({len(self.actions)} actions)")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to load macro from {path}: {str(e)}")
            return False
    
    def get_actions(self) -> List[MacroAction]:
        """Get the list of recorded actions."""
        return self.actions.copy()
    
    def clear(self):
        """Clear all recorded actions."""
        self.actions = []
        self.macro_name = ""
        self.start_time = None


class MacroPlayer:
    """
    Plays back recorded macros with context substitution and error handling.
    """
    
    def __init__(self, driver, logger=None):
        """
        Initialize the macro player.
        
        Args:
            driver: Selenium WebDriver instance
            logger: Optional logging function
        """
        self.driver = driver
        self.logger = logger or logging.info
        self._stop_requested = False
        self._pause_requested = False
        self.current_action_index = 0
        self.screenshot_dir = Path("logs/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    def stop(self):
        """Request playback to stop."""
        self._stop_requested = True
        self.logger("🛑 Playback stop requested")
    
    def pause(self):
        """Request playback to pause."""
        self._pause_requested = True
        self.logger("⏸️ Playback pause requested")
    
    def resume(self):
        """Resume playback after pause."""
        self._pause_requested = False
        self.logger("▶️ Playback resumed")
    
    def _apply_template(self, text: str, context: Dict[str, str]) -> str:
        """
        Apply context substitution to template strings.
        
        Args:
            text (str): Template string with placeholders like {invoice_number}
            context (dict): Context dictionary with values
            
        Returns:
            str: String with placeholders replaced
        """
        if not text:
            return text
        
        try:
            return text.format(**context)
        except KeyError as e:
            self.logger(f"⚠️ Missing context key: {e}")
            return text
        except Exception as e:
            self.logger(f"⚠️ Template substitution error: {e}")
            return text
    
    def play(self, actions: List[MacroAction], context: Dict[str, str] = None, 
             dry_run: bool = False, step_delay: float = 0.5) -> Dict[str, Any]:
        """
        Play back a list of macro actions.
        
        Args:
            actions (list): List of MacroAction objects
            context (dict): Context for template substitution
            dry_run (bool): If True, only validate without executing state-changing actions
            step_delay (float): Delay between actions in seconds
            
        Returns:
            dict: Playback results including success status and statistics
        """
        context = context or {}
        self._stop_requested = False
        self._pause_requested = False
        self.current_action_index = 0
        
        results = {
            "success": False,
            "total_actions": len(actions),
            "completed_actions": 0,
            "failed_actions": 0,
            "errors": []
        }
        
        self.logger(f"▶️ Starting macro playback ({len(actions)} actions)")
        if dry_run:
            self.logger("🔍 DRY RUN MODE - No state-changing actions will be executed")
        
        for idx, act in enumerate(actions):
            self.current_action_index = idx
            
            # Check for stop request
            if self._stop_requested:
                self.logger("🛑 Playback stopped by user")
                break
            
            # Check for pause request
            while self._pause_requested:
                time.sleep(0.1)
            
            # Apply delay between actions
            if idx > 0 and step_delay > 0:
                time.sleep(step_delay)
            
            # Log action
            desc = act.description or f"{act.action} on {act.selector[:50]}"
            self.logger(f"[{idx+1}/{len(actions)}] {desc}")
            
            # Skip state-changing actions in dry run
            if dry_run and act.action in ["send_keys", "click", "submit"]:
                self.logger(f"  ⏭️ Skipped (dry run)")
                results["completed_actions"] += 1
                continue
            
            # Execute action with retries
            success = self._execute_action_with_retry(act, context)
            
            if success:
                results["completed_actions"] += 1
            else:
                results["failed_actions"] += 1
                results["errors"].append({
                    "action_index": idx,
                    "action": act.action,
                    "description": desc,
                    "error": "Failed after retries"
                })
                
                # Capture screenshot on failure
                self._capture_screenshot(f"error_action_{idx}")
                
                # Decide whether to continue or stop
                if act.meta.get("critical", False):
                    self.logger(f"❌ Critical action failed, stopping playback")
                    break
        
        results["success"] = results["failed_actions"] == 0
        
        summary = f"✅ Playback complete: {results['completed_actions']}/{results['total_actions']} actions succeeded"
        if results["failed_actions"] > 0:
            summary = f"⚠️ Playback completed with errors: {results['failed_actions']} actions failed"
        
        self.logger(summary)
        return results
    
    def _execute_action_with_retry(self, act: MacroAction, context: Dict[str, str]) -> bool:
        """
        Execute a single action with retry logic.
        
        Args:
            act (MacroAction): Action to execute
            context (dict): Context for template substitution
            
        Returns:
            bool: True if action succeeded
        """
        value = self._apply_template(act.value or "", context)
        max_retries = max(1, act.retries)
        
        for attempt in range(max_retries):
            try:
                if act.action == "navigate":
                    url = self._apply_template(act.value, context)
                    self.driver.get(url)
                    
                elif act.action == "click":
                    element = self._find_element(act)
                    element.click()
                    
                elif act.action == "send_keys":
                    element = self._find_element(act)
                    element.clear()
                    element.send_keys(value)
                    
                elif act.action == "send_keys_append":
                    element = self._find_element(act)
                    element.send_keys(value)
                    
                elif act.action == "wait":
                    wait_time = float(value or act.timeout)
                    time.sleep(wait_time)
                    
                elif act.action == "wait_for_element":
                    self._wait_for_element(act)
                    
                elif act.action == "assert_text":
                    element = self._find_element(act)
                    if value not in element.text:
                        raise AssertionError(f"Expected text '{value}' not found in element")
                    
                elif act.action == "assert_element":
                    self._find_element(act)  # Will raise exception if not found
                    
                elif act.action == "screenshot":
                    filename = value or f"screenshot_{int(time.time())}"
                    self._capture_screenshot(filename)
                    
                elif act.action == "get_text":
                    element = self._find_element(act)
                    text = element.text
                    self.logger(f"  📄 Element text: {text[:100]}")
                    
                else:
                    self.logger(f"  ⚠️ Unknown action type: {act.action}")
                    return False
                
                # Action succeeded
                return True
                
            except Exception as e:
                attempt_num = attempt + 1
                if attempt_num < max_retries:
                    wait_time = min(2 ** attempt, 10)  # Exponential backoff, max 10s
                    self.logger(f"  ⚠️ Attempt {attempt_num}/{max_retries} failed: {str(e)[:100]}")
                    self.logger(f"  ⏳ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.logger(f"  ❌ Action failed after {max_retries} attempts: {str(e)[:100]}")
                    logging.error(f"Action failed: {act.action} - {str(e)}")
        
        return False
    
    def _find_element(self, act: MacroAction):
        """
        Find element using selector.
        
        Args:
            act (MacroAction): Action containing selector info
            
        Returns:
            WebElement: Found element
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        by_type = By.XPATH if act.selector_type == "xpath" else By.CSS_SELECTOR
        
        # Wait for element to be present
        element = WebDriverWait(self.driver, act.timeout).until(
            EC.presence_of_element_located((by_type, act.selector))
        )
        
        return element
    
    def _wait_for_element(self, act: MacroAction):
        """
        Wait for element to be visible/clickable.
        
        Args:
            act (MacroAction): Action containing selector info
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        by_type = By.XPATH if act.selector_type == "xpath" else By.CSS_SELECTOR
        condition_type = act.meta.get("condition", "visible")
        
        if condition_type == "clickable":
            WebDriverWait(self.driver, act.timeout).until(
                EC.element_to_be_clickable((by_type, act.selector))
            )
        else:  # visible
            WebDriverWait(self.driver, act.timeout).until(
                EC.visibility_of_element_located((by_type, act.selector))
            )
    
    def _capture_screenshot(self, filename: str):
        """
        Capture browser screenshot.
        
        Args:
            filename (str): Base filename for screenshot
        """
        try:
            filepath = self.screenshot_dir / f"{filename}_{int(time.time())}.png"
            self.driver.save_screenshot(str(filepath))
            self.logger(f"  📸 Screenshot saved: {filepath.name}")
        except Exception as e:
            self.logger(f"  ⚠️ Failed to capture screenshot: {str(e)}")


class MacroLibrary:
    """
    Manages a library of saved macros.
    """
    
    def __init__(self, library_path: str = "macros"):
        """
        Initialize macro library.
        
        Args:
            library_path (str): Directory to store macro files
        """
        self.library_path = Path(library_path)
        self.library_path.mkdir(parents=True, exist_ok=True)
    
    def list_macros(self) -> List[Dict[str, Any]]:
        """
        List all available macros in the library.
        
        Returns:
            list: List of macro metadata dictionaries
        """
        macros = []
        
        for macro_file in self.library_path.glob("*.json"):
            try:
                with open(macro_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                macros.append({
                    "filename": macro_file.name,
                    "path": str(macro_file),
                    "name": data.get("name", macro_file.stem),
                    "created_at": data.get("created_at", ""),
                    "action_count": data.get("action_count", 0),
                    "version": data.get("version", 1)
                })
            except Exception as e:
                logging.warning(f"Failed to read macro {macro_file}: {str(e)}")
        
        return sorted(macros, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def get_macro_path(self, macro_name: str) -> str:
        """
        Get full path for a macro file.
        
        Args:
            macro_name (str): Name of the macro
            
        Returns:
            str: Full file path
        """
        if not macro_name.endswith(".json"):
            macro_name += ".json"
        
        return str(self.library_path / macro_name)
    
    def delete_macro(self, macro_name: str) -> bool:
        """
        Delete a macro from the library.
        
        Args:
            macro_name (str): Name of the macro to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            path = Path(self.get_macro_path(macro_name))
            if path.exists():
                path.unlink()
                logging.info(f"🗑️ Deleted macro: {macro_name}")
                return True
            return False
        except Exception as e:
            logging.error(f"Failed to delete macro {macro_name}: {str(e)}")
            return False
