# Frontend setup

```BASH
mkdir frontend && cd frontend
npx degit sveltejs/template svelte-app
cd svelte-app
npm install

# Move the contents of the svelte-app directory to the frontend directory and remove the svelte-app directory
cd ..
mv svelte-app/* .
mv svelte-app/.* .
rmdir svelte-app

# Upgrade Svelte from "^3.55.0" to "^5.0.0"

# remove node_modules and package-lock.json:
rm -rf node_modules
rm package-lock.json
# Specify version "^5.0.0" for svelte in package.json
# manually bump of version for all dependencies as well.

npm install
npm list svelte
# test the app still works:
npm run dev
```
