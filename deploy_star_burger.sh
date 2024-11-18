set -Eeuo pipefail

cd /opt/django/star-burger
echo "Updating code from git..."
git pull

echo "Installing pip requirements..."
.venv/bin/pip3 install -r requirements.txt

echo "Installing Node.js packets"
npm ci --dev

echo "Fixing npm"
npm audit fix

echo "Updating browserslist db"
npx browserslist@latest --update-db

echo "Building JS with Parcel..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Collecting static files..."
.venv/bin/python3 manage.py collectstatic --noinput

echo "Running migrations..."
.venv/bin/python3 manage.py migrate

echo "Reloading services..."
for service in nginx.service postgresql@17-main.service star-burger.service; do
        sudo systemctl reload $service
done

echo "Notify rollbar about deploy"
REVISION=$(git rev-parse --short HEAD)
ROLLBAR_TOKEN=$(cat .env | grep ROLLBAR_TOKEN | cut -d "=" -f 2)
curl -H "Accept: application/json" \
-H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
-H "Content-Type: application/json" \
-X POST 'https://api.rollbar.com/api/1/deploy' \
-d '{"environment": "production", "revision": "'"$REVISION"'", "rollbar_name": "aleksandr", "local_username": "a-skripko", "status": "succeeded"}'

git commit -m "Deploy $REVISION"

echo "Deploy $REVISION is finished successfully"
