GIMX_SUPPORTED_DEB=gimx_7.10-1_armhf.deb

build/$(GIMX_SUPPORTED_DEB):
	mkdir -p build
	wget -O $@ "https://github.com/matlo/GIMX/releases/download/v7.10/$(GIMX_SUPPORTED_DEB)"

installer.tar.gz: install.sh build/$(GIMX_SUPPORTED_DEB) version.txt auto_updater/update.sh auto_updater/download.sh auto_updater/getLatestReleaseNumber.sh
	tar -czvf $@ --exclude='*.pyc' $^ src
