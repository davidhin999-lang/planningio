# Admin Password Setup

## Set Admin Password in Vercel

To enable the admin panel with password `spellingbee2024`:

### Steps:

1. Go to https://vercel.com/dashboard
2. Select your project: **lasalle-spelling-bee**
3. Click **Settings** → **Environment Variables**
4. Add a new environment variable:
   - **Name:** `ADMIN_PASSWORD`
   - **Value:** `spellingbee2024`
5. Click **Save**
6. Trigger a redeploy:
   - Go to **Deployments** tab
   - Click **Redeploy** on the latest deployment
   - Or push a new commit to trigger auto-deploy

### Verification

Once deployed, you can test the admin login at:
- https://lasalle-spelling-bee.vercel.app/admin
- Username: (any username)
- Password: `spellingbee2024`

### Security Note

The password is now stored securely in Vercel's environment variables and is NOT exposed in the codebase or GitHub repository.
