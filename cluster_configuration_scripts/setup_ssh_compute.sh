sudo usermod -s /bin/bash nova
sudo mkdir -p -m 700 /var/lib/nova/.ssh
echo -e "Host *\nStrictHostKeyChecking no" | sudo tee /var/lib/nova/.ssh/config
sudo cp ~/.ssh/authorized* /var/lib/nova/.ssh/
sudo cp ~/graybox.pem /var/lib/nova/.ssh/id_rsa
sudo chown -R nova:nova /var/lib/nova/.ssh/

