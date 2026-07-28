# TC-007 — Frontend Screens 1–5 render and interaction behavior

**Automated by:** `frontend/src/features/auth/*.test.jsx`, `frontend/src/api/authClient.test.js`

## Steps (representative, per screen)
1. **RegisterPage (Screen 1)**: submit disabled until a role is selected; successful
   register+login navigates to `/home`; a rejected register call shows an inline error.
2. **LoginPage (Screen 2)**: successful login navigates to `/home`; an `account_blocked`
   error navigates to `/blocked`; any other error shows an inline error banner.
3. **RoleHomePage (Screen 3)**: shows "Not logged in" with no session; shows a session banner
   with role + email (fetched via `/me`) once logged in.
4. **UdidVerificationModal (Screen 4)**: successful verification calls `onResolved(true)`;
   a failed verification shows an inline error; the skip button calls `onResolved(false)`.
5. **AccountBlockedPage (Screen 5)**: renders the blocked message and a working support link.
6. **authClient**: returns `data` on success; throws an error carrying `status`/`code`/`body`
   on failure; correctly URL-encodes the CARS callback code.

## Expected result
All interactions above behave exactly as described; no unhandled exceptions, no console errors
beyond the known React Router v7 future-flag deprecation warnings.

## Pass/fail criteria
Pass if all 17 automated frontend tests across these 6 areas pass.

## Explicitly not covered here
Real-browser visual verification of these screens — deferred to Step 7
(`/end-to-end-testing-and-bug-resolution-for-this-story`), since this environment has no browser
available for interactive manual testing.
