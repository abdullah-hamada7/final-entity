You are a senior frontend engineer responsible for diagnosing and fixing a global layout bug in a web application.

Problem Description
A blank horizontal space appears at the very top of every page of the website when viewed on mobile devices. The space appears between the browser/status bar and the page header/navigation bar. It looks like an empty container or incorrect spacing that pushes the content downward.

This issue occurs consistently across all pages of the application, not just a single view.

Observed Behavior
- A white/empty horizontal area appears above the header.
- The header (logo + menu icon) is pushed down.
- The gap exists on all pages of the site.
- The issue appears mainly on mobile devices.
- The rest of the layout functions normally.

Expected Behavior
- The header should be aligned directly below the browser safe area.
- No extra margin, padding, or empty container should appear above the header.
- The layout should respect mobile safe areas but not create extra spacing.

Tasks
1. Inspect the global layout structure.
2. Check the following possible causes:
   - Global CSS margin or padding on `body` or `html`.
   - Incorrect `padding-top` or `margin-top` in the header container.
   - Safe-area handling (`env(safe-area-inset-top)` or `constant(safe-area-inset-top)`).
   - Incorrect positioning (`position: fixed` or `sticky`) on the header.
   - Extra wrapper div added by layout components.
   - Incorrect height set on navigation bars.
3. Identify the root cause in the shared layout component that affects all pages.
4. Fix the issue at the global layout level so it is resolved everywhere.
5. Ensure the fix works across:
   - mobile browsers
   - iOS Safari
   - Android Chrome
6. Ensure no layout shifts occur after the fix.

Constraints
- Do not apply page-specific fixes.
- The solution must be implemented in the global layout/header component.
- Maintain responsiveness across all screen sizes.

Deliverables
1. Root cause explanation.
2. Code fix.
3. Updated CSS/layout structure.
4. Verification steps to confirm the issue is resolved across all pages.