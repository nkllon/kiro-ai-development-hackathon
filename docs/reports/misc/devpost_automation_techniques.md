# DevPost Automation Techniques - Successful Methods

## Overview
This document captures the working techniques for automating DevPost hackathon submission forms using AppleScript and Chrome DevTools Protocol.

## Key Success Patterns

### 1. Navigation Strategy
- **Use Chrome's built-in find function** instead of trying to click specific elements
- **Pattern**: `window.find("text", false, false, true, false, true, false)`
- **Then click on selection**: Get selection range and click the parent element
- **Why it works**: More reliable than trying to find specific CSS selectors

### 2. Form Field Filling
- **Direct field targeting**: Use `document.querySelector("input[name='exact_name']")`
- **Focus before filling**: Always call `field.focus()` before setting value
- **Trigger events**: Dispatch both 'input' and 'change' events after setting value
- **Pattern**:
```javascript
var field = document.querySelector("input[name='field_name']");
if(field) {
    field.focus();
    field.value = "new_value";
    field.dispatchEvent(new Event("input", {bubbles: true}));
    field.dispatchEvent(new Event("change", {bubbles: true}));
}
```

### 3. Precise UI Interaction
- **Tab navigation**: Use `key code 48` (Tab) to navigate between fields
- **Enter to submit**: Use `key code 36` (Enter) to click focused buttons
- **Arrow keys for positioning**: Use arrow keys when cursor is "5mm off"
- **Direct typing**: Use `keystroke` for direct text input when focus is correct

### 4. Field Discovery
- **Find empty required fields**: Query `input[required], textarea[required], select[required]`
- **Check for empty values**: Filter out fields with existing values
- **Log field names**: Use `console.log()` to identify field names for targeting

## Successful Field Mappings

### Project Overview Section
- **Title**: `input[name="participants_manage_project_overview[title]"]`
- **Tagline**: `input[name="participants_manage_project_overview[tagline]"]`

### Project Details Section  
- **Tags**: `input[name="software[tag_list]"]`
- **Video URL**: `input[name="software[video_url]"]`

### Submission Requirements
- **Title**: `input[name="participants_submission_requirements[submission_field_values_attributes][1][value]"]`
- **Description**: `textarea[name="participants_submission_requirements[submission_field_values_attributes][5][value]"]`
- **Project URL**: `input[name="participants_submission_requirements[submission_field_values_attributes][7][value]"]`
- **Demo Video**: `input[name="participants_submission_requirements[submission_field_values_attributes][13][value]"]`

## AppleScript Commands That Work

### Focus Chrome
```applescript
tell application "Google Chrome" to activate
```

### Execute JavaScript
```applescript
tell application "Google Chrome"
    tell active tab of front window
        execute javascript "your_javascript_here"
    end tell
end tell
```

### System Events (Key Presses)
```applescript
tell application "System Events"
    key code 48  # Tab
    key code 36  # Enter
    keystroke "text"  # Direct typing
end tell
```

## Error Patterns to Avoid

1. **Don't restart Chrome** - Always work with existing session
2. **Don't create new tabs** - Use existing page
3. **Don't assume element selectors** - Always inspect first
4. **Don't skip focus()** - Fields won't accept values without focus
5. **Don't forget event dispatch** - Form validation needs triggered events

## Debugging Techniques

1. **Console logging**: Add `console.log()` statements to track progress
2. **Element inspection**: Use `document.querySelector()` to verify elements exist
3. **Value checking**: Log field values before and after setting
4. **Selection checking**: Verify `window.getSelection()` works for navigation

## Session Preservation

- **Never restart Chrome** with debugging enabled unless absolutely necessary
- **Extract cookies/session data** before any restart attempts
- **Use existing browser instance** - connect via CDP if needed
- **Preserve user data directory** - don't use temporary profiles

## Final Submission Checklist

1. ✅ All required fields filled
2. ✅ No red indicators on page
3. ✅ All sections complete (Additional Info, Project Overview, Project Details, Built With)
4. ✅ Valid video URL (placeholder acceptable for draft)
5. ✅ Save and Continue clicked
6. ✅ Confirmation received

## Key Insight
The breakthrough was realizing that **Chrome's built-in find function** + **selection clicking** is more reliable than trying to target specific CSS selectors for navigation elements. This approach works because it leverages the browser's own text search capabilities rather than trying to reverse-engineer the DOM structure.
