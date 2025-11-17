from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
import os
import pvporcupine

# Get the pvporcupine package directory
pvporcupine_dir = os.path.dirname(pvporcupine.__file__)

# Start with PyInstaller's utility (but it may only collect directories)
datas = collect_data_files('pvporcupine')

# CRITICAL: Manually walk and collect ALL individual files in resources
# collect_data_files may only return directories, not individual files
resources_path = os.path.join(pvporcupine_dir, 'resources')
if os.path.exists(resources_path):
    # Create a set to track what we've added (using normalized paths)
    # PyInstaller format: (source_full_path, dest_relative_path)
    existing_dests = set()
    for src_full, dest_rel in datas:
        # Normalize the destination path for comparison
        normalized = dest_rel.replace('\\', '/').lower()
        existing_dests.add(normalized)
    
    # Walk through ALL files in resources and add them individually
    # PyInstaller format: (source_full_path, dest_relative_path)
    for root, dirs, files in os.walk(resources_path):
        for file in files:
            src_full = os.path.join(root, file)
            # Preserve directory structure relative to pvporcupine package
            rel_path = os.path.relpath(src_full, pvporcupine_dir)
            # Destination path uses backslashes on Windows (PyInstaller format)
            dest_rel = os.path.join('pvporcupine', rel_path)
            normalized_dest = dest_rel.replace('\\', '/').lower()
            
            # Only add if not already in datas
            if normalized_dest not in existing_dests:
                # PyInstaller format: (source_full_path, dest_relative_path)
                datas.append((src_full, dest_rel))
                existing_dests.add(normalized_dest)

# Collect dynamic libraries
binaries = collect_dynamic_libs('pvporcupine')

# Debug output
print(f"[hook-pvporcupine] Collected {len(datas)} data files from pvporcupine")
if datas:
    # Show a few examples
    print(f"[hook-pvporcupine] Sample files:")
    for src_full, dest_rel in datas[:5]:
        print(f"  {dest_rel} <- {src_full[:60]}...")
    
    # Check specifically for windows keyword files
    # PyInstaller format: (source_full_path, dest_relative_path)
    windows_files = [d for _, d in datas if 'windows' in d.lower() and d.endswith('.ppn')]
    if windows_files:
        print(f"[hook-pvporcupine] Found {len(windows_files)} Windows keyword files")
        print(f"[hook-pvporcupine] Example: {windows_files[0]}")
    else:
        print(f"[hook-pvporcupine] WARNING: No Windows keyword files found!")

