#GIMX_SUPPORTED_DEB=gimx_7.10-1_armhf.deb
#build/$(GIMX_SUPPORTED_DEB):
#	mkdir -p build
#	wget -O $@ "https://github.com/matlo/GIMX/releases/download/v7.10/$(GIMX_SUPPORTED_DEB)"

GIMX_VERSION=7.12+

installer.tar.gz: install.sh build/gimx_$(GIMX_VERSION)-1_armhf_original.deb version.txt auto_updater/update.sh
	tar -czvf $@ --exclude='*.pyc' $^ src

installer-special.tar.gz: install.sh build/gimx_$(GIMX_VERSION)+-1_armhf_special.deb version.txt auto_updater/update.sh
	tar -czvf $@ --exclude='*.pyc' $^ src

installer-all.tar.gz: install.sh build/gimx_$(GIMX_VERSION)-1_armhf_original.deb build/gimx_$(GIMX_VERSION)+-1_armhf_special.deb version.txt auto_updater/update.sh
	tar -czvf $@ --exclude='*.pyc' $^ src
