# Revamp Design:
## Componenets
### Interface
* [Google Home Mini actions](https://medium.com/google-cloud/building-your-first-action-for-google-home-in-30-minutes-ec6c65b7bd32)
* Sends https POST requests to localhost webhook
* In future: UI to view features of life-bot through browser

### Backend
* Flask app running on raspberry pi
* Webhook on localhost
* [Email tools](https://realpython.com/python-send-email/)
  * Gmail account for bot
  * [Alias for this specific app](https://support.google.com/domains/answer/9437157?hl=en)
* Storage API

### Storage Options
* *[Google Drive](https://developers.google.com/drive/api/v3/about-sdk)*
  * Bot account = 15GB of storage
* Github Private Repo
  * [Storage limit 1GB](https://docs.github.com/en/github/managing-large-files/about-storage-and-bandwidth-usage)
* Some paid service
  * Google Cloud
  * AWS
  * Linode
