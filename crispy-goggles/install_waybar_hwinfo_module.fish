#!/usr/bin/env fish
# Waybar Hardware Info Module Installer
# Safely integrates hw_info_module.py, CSS, and config into user's Waybar setup.
# Idempotent, robust, and fish-shell compatible.

set -l MODULE_SRC (realpath hw_info_module.py)
set -l MODULE_DEST ~/.config/waybar/modules/hw_info_module.py
set -l CSS_SRC (realpath waybar_hwinfo_style.css)
set -l CSS_DEST ~/.config/waybar/style.css
set -l CONFIG_SNIPPET (realpath waybar_config_snippet.jsonc)
set -l CONFIG_DEST ~/.config/waybar/config.jsonc
set -l BACKUP_SUFFIX (date +%Y%m%d_%H%M%S)

function backup_file
    set -l file $argv[1]
    if test -e $file
        cp $file $file.bak.$BACKUP_SUFFIX
        echo "Backed up $file to $file.bak.$BACKUP_SUFFIX"
    end
end

# 1. Copy Python module
if not test -d ~/.config/waybar/modules
    mkdir -p ~/.config/waybar/modules
end
if not test -e $MODULE_DEST
    cp $MODULE_SRC $MODULE_DEST
    echo "Copied $MODULE_SRC to $MODULE_DEST"
else
    echo "$MODULE_DEST already exists. Skipping copy."
end

# 2. Append CSS if not present
if not test -e $CSS_DEST
    touch $CSS_DEST
end
set -l CSS_SNIPPET (cat $CSS_SRC)
if not string match -q '*#custom-hwinfo*' (cat $CSS_DEST)
    backup_file $CSS_DEST
    echo "$CSS_SNIPPET" >> $CSS_DEST
    echo "Appended hardware info CSS to $CSS_DEST"
else
    echo "CSS for #custom-hwinfo already present in $CSS_DEST. Skipping."
end

# 3. Insert config snippet using jq
if not type -q jq
    echo "jq is required for JSON editing. Please install jq and re-run this script."
    exit 1
end
if not test -e $CONFIG_DEST
    echo '{"modules-left":[],"custom/hwinfo":{}}' > $CONFIG_DEST
end
backup_file $CONFIG_DEST
set -l SNIPPET (cat $CONFIG_SNIPPET | string replace '/path/to/your/hw_info_module.py' $MODULE_DEST)
# Add/merge custom/hwinfo config
jq --argjson snip "$SNIPPET" '(. + $snip)' $CONFIG_DEST > $CONFIG_DEST.tmp && mv $CONFIG_DEST.tmp $CONFIG_DEST
# Ensure "custom/hwinfo" is in modules-left
set -l in_left (jq -r '."modules-left"[]?' $CONFIG_DEST | string match -r '^custom/hwinfo$')
if test -z "$in_left"
    jq '."modules-left" += ["custom/hwinfo"] | ."modules-left" |= unique' $CONFIG_DEST > $CONFIG_DEST.tmp && mv $CONFIG_DEST.tmp $CONFIG_DEST
    echo 'Added "custom/hwinfo" to "modules-left".'
else
    echo '"custom/hwinfo" already present in "modules-left".'
end

echo "Waybar hardware info module integration complete. Restart Waybar to see changes."
