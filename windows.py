from Foundation import *
from AppKit import *
import objc

# Constants
NSTabViewTypeTopTabsBezelBorder = 0
NSTabViewTypeLeftTabsBezelBorder = 1
NSTabViewTypeBottomTabsBezelBorder = 2
NSTabViewTypeRightTabsBezelBorder = 3
NSTabViewTypeNoTabsBezelBorder = 4
NSTabViewTypeNoTabsLineBorder = 5
NSTabViewTypeNoTabsNoBorder = 6

NSWindowStyleMaskTitled = 1 << 0
NSWindowStyleMaskClosable = 1 << 1
NSWindowStyleMaskMiniaturizable = 1 << 2
NSWindowStyleMaskResizable = 1 << 3

NSButtonTypeSwitch = 3
NSBezelStyleRounded = 1
NSOnState = 1
NSOffState = 0
NSTextFieldSquareBezel = 1
NSBackingStoreBuffered = 2

class CircularProgressView(NSView):
    def initWithFrame_progress_(self, frame: NSRect, progress: float):
        self = objc.super(CircularProgressView, self).initWithFrame_(frame)
        if self is None: return None
        self.progress = progress
        self._tag = 0
        return self

    def init(self):
        self = objc.super(CircularProgressView, self).init()
        if self is None: return None
        self.progress = 0.0
        self._tag = 0
        return self

    def tag(self) -> int:
        return self._tag

    def setTag_(self, tag: int):
        self._tag = tag

    def drawRect_(self, dirtyRect):
        if not self.progress:
            self.progress = 0.0
            
        context = NSGraphicsContext.currentContext()
        
        # Calculate dimensions
        bounds = self.bounds()
        center_x = bounds.size.width / 2
        center_y = bounds.size.height / 2
        radius = min(center_x, center_y) - 10
        
        # Draw background circle
        circle_path = NSBezierPath.bezierPath()
        circle_path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_(
            NSPoint(center_x, center_y), radius, 0, 360
        )
        NSColor.lightGrayColor().setStroke()
        circle_path.setLineWidth_(8)
        circle_path.stroke()
        
        # Draw progress arc
        if self.progress > 0:
            progress_path = NSBezierPath.bezierPath()
            end_angle = 360 * (1 - self.progress)  # Reversed to go clockwise
            progress_path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_(
                NSPoint(center_x, center_y), radius, 90, end_angle + 90
            )
            NSColor.systemBlueColor().setStroke()
            progress_path.setLineWidth_(8)
            progress_path.stroke()

class ProgressWindowController(NSWindowController):
    @objc.python_method
    def init(self):
        self = objc.super(ProgressWindowController, self).init()
        if self is None: return None
        return self

    def initWithProgress_total_type_count_next_(self, progress: int, total: int, 
                                              type: str, count: int, next: str) -> None:
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 360, 400),
            NSWindowStyleMaskTitled | 
            NSWindowStyleMaskClosable | 
            NSWindowStyleMaskMiniaturizable,
            NSBackingStoreBuffered,
            False
        )
        self = objc.super(ProgressWindowController, self).initWithWindow_(window)
        if self is None: return None
        
        window.setTitle_("Pomodoro Progress")
        self.progress = progress
        self.total = total
        self.type = type
        self.count = count
        self.next = next
        
        self.setupUIWithProgress(progress, total, type, count, next)
        window.center()
        return self

    def updateProgress_(self, current_time: int):
        window = self.window()
        if not window:
            return
            
        content_view = window.contentView()
        
        # Update time label
        time_label = content_view.viewWithTag_(1)
        if time_label:
            time_label.setStringValue_(f"{current_time // 60:02d}:{current_time % 60:02d}")
        
        # Update progress view
        progress_view = content_view.viewWithTag_(2)
        if progress_view:
            progress_view.progress = float(current_time) / float(self.total)
            progress_view.setNeedsDisplay_(True)

    @objc.python_method
    def setupUIWithProgress(self, current_time, total_time, session_type, 
                          session_count, next_session):
        window = self.window()
        content_view = window.contentView()
        
        # Session type and time
        session_label = NSTextField.labelWithString_(
            f"Current {session_type} Session"
        )
        session_label.setFrame_(NSMakeRect(20, 350, 320, 24))
        session_label.setFont_(NSFont.boldSystemFontOfSize_(13))
        session_label.setAlignment_(NSTextAlignmentCenter)
        
        # Time remaining
        time_label = NSTextField.labelWithString_(
            f"{current_time // 60:02d}:{current_time % 60:02d}"
        )
        time_label.setFrame_(NSMakeRect(20, 320, 320, 30))
        time_label.setFont_(NSFont.systemFontOfSize_(24))
        time_label.setAlignment_(NSTextAlignmentCenter)
        
        # Circular progress indicator
        progress = float(total_time - current_time) / float(total_time)
        progress_view = CircularProgressView.alloc().initWithFrame_progress_(
            NSMakeRect(80, 120, 200, 200),  # Centered, large circle
            progress
        )
        
        # Next session info
        next_label = NSTextField.labelWithString_(
            f"Next: {next_session}"
        )
        next_label.setFrame_(NSMakeRect(20, 80, 320, 24))
        next_label.setAlignment_(NSTextAlignmentCenter)
        
        # Session count
        count_label = NSTextField.labelWithString_(
            f"Session {session_count}"
        )
        count_label.setFrame_(NSMakeRect(20, 40, 320, 24))
        count_label.setAlignment_(NSTextAlignmentCenter)
        
        # Add all views
        content_view.addSubview_(session_label)
        content_view.addSubview_(time_label)
        content_view.addSubview_(progress_view)
        content_view.addSubview_(next_label)
        content_view.addSubview_(count_label)

        # Add tags to views we need to update
        time_label.setTag_(1)
        progress_view.setTag_(2)

class SettingsWindowController(NSWindowController):
    @objc.python_method
    def init(self):
        self = objc.super(SettingsWindowController, self).init()
        if self is None: return None
        return self

    def initWithSettings_callback_(self, settings: dict, callback: callable) -> None:
        self = self.init()
        if self is None: return None
        
        # Create window
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 480, 360),
            NSWindowStyleMaskTitled | 
            NSWindowStyleMaskClosable | 
            NSWindowStyleMaskMiniaturizable,
            NSBackingStoreBuffered,
            False
        )
        window.setTitle_("Pomodoro Settings")
        self.setWindow_(window)
        
        self.settings = settings
        self.callback = callback
        self.setupUI()
        window.center()
        return self

    @objc.python_method
    def setupUI(self):
        window = self.window()
        content_view = window.contentView()
        
        # Create tab view with adjusted position and size
        tab_view = NSTabView.alloc().initWithFrame_(
            NSMakeRect(20, 50, 440, 270)  # Adjusted y position and height
        )
        tab_view.setTabViewType_(NSTabViewTypeTopTabsBezelBorder)
        
        # Intervals Tab with adjusted position
        intervals_tab = NSTabViewItem.alloc().initWithIdentifier_("intervals")
        intervals_tab.setLabel_("Intervals")
        intervals_view = NSView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 440, 240)  # Adjusted height
        )
        
        # Create form layout for intervals
        y_pos = 200
        labels = [
            ("Work Duration:", "minutes"),
            ("Short Break:", "minutes"),
            ("Long Break:", "minutes"),
            ("Sessions before Long Break:", "sessions"),
            ("Daily Target:", "sessions")
        ]
        self.interval_inputs = {}
        
        for label, suffix_text in labels:
            # Label
            label_field = NSTextField.labelWithString_(label)
            label_field.setFrame_(NSMakeRect(20, y_pos, 160, 24))
            
            # Input field
            input_field = NSTextField.alloc().initWithFrame_(
                NSMakeRect(190, y_pos, 60, 24)
            )
            input_field.setBezeled_(True)
            input_field.setBezelStyle_(NSTextFieldSquareBezel)
            input_field.setDrawsBackground_(True)
            
            # Suffix label
            suffix = NSTextField.labelWithString_(suffix_text)
            suffix.setFrame_(NSMakeRect(260, y_pos, 60, 24))
            intervals_view.addSubview_(suffix)
            
            intervals_view.addSubview_(label_field)
            intervals_view.addSubview_(input_field)
            self.interval_inputs[label] = input_field
            y_pos -= 35
        
        intervals_tab.setView_(intervals_view)
        tab_view.addTabViewItem_(intervals_tab)
        
        # General Tab
        general_tab = NSTabViewItem.alloc().initWithIdentifier_("general")
        general_tab.setLabel_("General")
        general_view = NSView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 440, 280)
        )
        
        # Launch at startup
        self.launch_checkbox = NSButton.alloc().initWithFrame_(
            NSMakeRect(20, 230, 200, 24)
        )
        self.launch_checkbox.setButtonType_(NSButtonTypeSwitch)
        self.launch_checkbox.setTitle_("Launch at startup")
        self.launch_checkbox.setState_(
            NSOnState if self.settings['general']['launch_at_startup'] 
            else NSOffState
        )
        
        # Shortcuts section
        shortcut_label = NSTextField.labelWithString_("Keyboard Shortcuts")
        shortcut_label.setFrame_(NSMakeRect(20, 180, 200, 24))
        shortcut_label.setFont_(NSFont.boldSystemFontOfSize_(13))
        
        # Start/Pause shortcut
        start_shortcut_label = NSTextField.labelWithString_("Start/Pause:")
        start_shortcut_label.setFrame_(NSMakeRect(20, 150, 100, 24))
        self.start_shortcut = NSTextField.alloc().initWithFrame_(
            NSMakeRect(130, 150, 150, 24)
        )
        
        # Skip shortcut
        skip_shortcut_label = NSTextField.labelWithString_("Skip Timer:")
        skip_shortcut_label.setFrame_(NSMakeRect(20, 120, 100, 24))
        self.skip_shortcut = NSTextField.alloc().initWithFrame_(
            NSMakeRect(130, 120, 150, 24)
        )
        
        general_view.addSubview_(self.launch_checkbox)
        general_view.addSubview_(shortcut_label)
        general_view.addSubview_(start_shortcut_label)
        general_view.addSubview_(self.start_shortcut)
        general_view.addSubview_(skip_shortcut_label)
        general_view.addSubview_(self.skip_shortcut)
        
        general_tab.setView_(general_view)
        tab_view.addTabViewItem_(general_tab)
        
        # Add tab view to window
        content_view.addSubview_(tab_view)
        
        # Add buttons
        cancel_button = NSButton.alloc().initWithFrame_(
            NSMakeRect(290, 20, 80, 32)
        )
        cancel_button.setTitle_("Cancel")
        cancel_button.setBezelStyle_(NSBezelStyleRounded)
        cancel_button.setAction_(objc.selector(self.cancelClick_, signature=b'v@:@'))
        cancel_button.setTarget_(self)
        
        save_button = NSButton.alloc().initWithFrame_(
            NSMakeRect(380, 20, 80, 32)
        )
        save_button.setTitle_("Save")
        save_button.setBezelStyle_(NSBezelStyleRounded)
        save_button.setKeyEquivalent_("\r")  # Enter key
        save_button.setAction_(objc.selector(self.saveClick_, signature=b'v@:@'))
        save_button.setTarget_(self)
        
        content_view.addSubview_(cancel_button)
        content_view.addSubview_(save_button)
        
        # Load current settings
        self.loadCurrentSettings()
    
    @objc.python_method
    def loadCurrentSettings(self):
        # Load interval settings
        self.interval_inputs["Work Duration:"].setStringValue_(
            str(self.settings['intervals']['work_duration'])
        )
        self.interval_inputs["Short Break:"].setStringValue_(
            str(self.settings['intervals']['short_break_duration'])
        )
        self.interval_inputs["Long Break:"].setStringValue_(
            str(self.settings['intervals']['long_break_duration'])
        )
        self.interval_inputs["Sessions before Long Break:"].setStringValue_(
            str(self.settings['intervals']['long_break_after'])
        )
        self.interval_inputs["Daily Target:"].setStringValue_(
            str(self.settings['intervals']['target_per_day'])
        )
        
        # Load general settings
        self.start_shortcut.setStringValue_(
            self.settings['general']['shortcut_start_pause']
        )
        self.skip_shortcut.setStringValue_(
            self.settings['general']['shortcut_skip']
        )
    
    @objc.IBAction
    def saveClick_(self, sender):
        try:
            # Update settings
            new_settings = self.settings.copy()
            
            # Update intervals
            new_settings['intervals']['work_duration'] = int(
                self.interval_inputs["Work Duration:"].stringValue()
            )
            new_settings['intervals']['short_break_duration'] = int(
                self.interval_inputs["Short Break:"].stringValue()
            )
            new_settings['intervals']['long_break_duration'] = int(
                self.interval_inputs["Long Break:"].stringValue()
            )
            new_settings['intervals']['long_break_after'] = int(
                self.interval_inputs["Sessions before Long Break:"].stringValue()
            )
            new_settings['intervals']['target_per_day'] = int(
                self.interval_inputs["Daily Target:"].stringValue()
            )
            
            # Update general settings
            new_settings['general']['launch_at_startup'] = bool(
                self.launch_checkbox.state()
            )
            new_settings['general']['shortcut_start_pause'] = \
                self.start_shortcut.stringValue()
            new_settings['general']['shortcut_skip'] = \
                self.skip_shortcut.stringValue()
            
            # Call callback with new settings
            self.callback(new_settings)
            
            # Close window
            self.close()
            
        except ValueError as e:
            # Show error alert
            alert = NSAlert.alloc().init()
            alert.setMessageText_("Invalid Input")
            alert.setInformativeText_("Please ensure all interval values are numbers.")
            alert.addButtonWithTitle_("OK")
            alert.runModal()
    
    @objc.IBAction
    def cancelClick_(self, sender):
        self.close()

class StatisticsWindowController(NSWindowController):
    def initWithStats_(self, stats):
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 400, 300),
            NSWindowStyleMaskTitled | 
            NSWindowStyleMaskClosable | 
            NSWindowStyleMaskMiniaturizable,
            NSBackingStoreBuffered,
            False
        )
        self = objc.super(StatisticsWindowController, self).initWithWindow_(window)
        if self is None: return None
        
        window.setTitle_("Pomodoro Statistics")
        self.setupUIWithStats(stats)
        window.center()
        return self

    @objc.python_method
    def setupUIWithStats(self, stats):
        window = self.window()
        content_view = window.contentView()
        
        # Today's stats
        today_label = NSTextField.labelWithString_("Today's Progress")
        today_label.setFrame_(NSMakeRect(20, 260, 360, 24))
        today_label.setFont_(NSFont.boldSystemFontOfSize_(13))
        
        sessions_label = NSTextField.labelWithString_(
            f"Completed Sessions: {stats.get('today_sessions', 0)}"
        )
        sessions_label.setFrame_(NSMakeRect(20, 230, 360, 24))
        
        work_time_label = NSTextField.labelWithString_(
            f"Total Work Time: {stats.get('today_work_time', '0:00')}"
        )
        work_time_label.setFrame_(NSMakeRect(20, 200, 360, 24))
        
        # Add views
        content_view.addSubview_(today_label)
        content_view.addSubview_(sessions_label)
        content_view.addSubview_(work_time_label)