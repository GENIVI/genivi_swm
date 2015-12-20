TARGET= swm_download_update.png \
	swm_local_media_update.png \
	swm_diagnostic_update.png \
	swm_process_install_package.png \
	swm_process_upgrade_package.png \
	swm_process_remove_package.png \
	swm_process_write_disk_partition.png \
	swm_process_patch_disk_partition.png \
	swm_process_create_disk_partition.png \
	swm_process_delete_disk_partition.png \
	swm_process_resize_disk_partition.png \
	swm_process_flash_module_firmware.png \
	swm_process_reboot.png \
	swm_process_start_components.png \
	swm_process_stop_components.png \
	swm_sc_get_installed_packages.png \
	swm_hmi_get_installed_packages.png 

.PHONY: all clean

%.png: %.msc
	mscgen -T png $<

all: $(TARGET)

clean:
	rm -f $(TARGET)
