# EOX core

Eox-core (or Edunext Open eXtensions) is a set of APIS for the [edx-platform](https://github.com/edx/edx-platform) to make changing the platform easier on commercial environments, including bulk creation of pre-activated users (e.g. skip sending an activation email) and many others.

## Installation
```bash
# Assuming ubuntu or similar dist
sudo apt-get install direnv
# Instructions for installing devstack on hawthorn 
cd ~/Documents/
mkdir eoxstack
cd eoxstack
git clone git@github.com:edx/devstack.git
cd devstack
git checkout open-release/hawthorn.master
export OPENEDX_RELEASE=hawthorn.master
make dev.checkout
make dev.clone
make dev.provision
make dev.provision
direnv allow .
echo export OPENEDX_RELEASE=hawthorn.master > .envrc
make dev.up
cd ~/Documents/eoxstack/src/
# Instructions for installing eox-core
sudo mkdir edxapp
cd edxapp
git clone git@github.com:eduNEXT/eox-core.git
cd ~/Documents/eoxstack/devstack
make lms-shell
# Instructions to run on docker virtual machine shell
sudo su edxapp -s /bin/bash
source /edx/app/edxapp/venvs/edxapp/bin/activate
cd /edx/src/edxapp/eox-core
pip install -e .
```
Then create the oauth client at http://localhost:18000/admin/oauth2/client/add/ and use the client-id and client-secret to call the eox-core API
