cd /c/Users/Manou/Documents/GitHub/colibri
eval $(ssh-agent -s)
ssh-add /c/Users/Manou/.ssh/github_rsa 
git fetch -a
git checkout v0.11
sleep 3

