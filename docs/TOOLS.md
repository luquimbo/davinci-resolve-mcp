# Tool Reference

Auto-generated on 2026-02-28 02:49 UTC by `scripts/generate_tool_docs.py`.

**189 tools** across **12 domains**.

## Table of Contents

- [Playback](#playback) (7 tools)
- [Project](#project) (21 tools)
- [Media Storage](#media-storage) (4 tools)
- [Media Pool](#media-pool) (14 tools)
- [Clips (Media Pool Item)](#clips-media-pool-item) (21 tools)
- [Timeline](#timeline) (29 tools)
- [Timeline Items](#timeline-items) (27 tools)
- [Render](#render) (14 tools)
- [Color](#color) (24 tools)
- [Fusion](#fusion) (11 tools)
- [Gallery](#gallery) (14 tools)
- [Fairlight](#fairlight) (3 tools)

## Playback

*Page navigation, timecode, playhead, version info*

### `playback_get_current_item` `read-only`

Return info about the timeline item under the playhead, or None.

Returns a dict with keys: name, start, end, duration.
Returns None if no item is under the playhead or no timeline is open.

### `playback_get_page` `read-only`

Return the name of the currently active Resolve page.

Possible values: "media", "cut", "edit", "fusion", "color",
"fairlight", "deliver", or "" if Resolve cannot determine the page.

### `playback_get_timecode` `read-only`

Return the current playhead timecode (e.g. "01:00:05:12").

Requires an open project with at least one timeline.

### `playback_open_page`

Switch Resolve to a different workspace page.

Args:
    page: Target page name.  Must be one of: media, cut, edit,
          fusion, color, fairlight, deliver.

Returns:
    True if the page switch succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `string` | *required* |  |

### `playback_set_timecode`

Move the playhead to a specific timecode position.

Args:
    timecode: Target timecode string, e.g. "01:00:05:12".
              Must match the project's timecode format.

Returns:
    True if the playhead was moved successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timecode` | `string` | *required* |  |

### `resolve_get_product` `read-only`

Return the Resolve product name.

Typically "DaVinci Resolve" (free) or "DaVinci Resolve Studio" (paid).

### `resolve_get_version` `read-only`

Return the DaVinci Resolve version as a dotted string (e.g. "19.1.2").

The underlying API may return a list of version components or a string;
this tool always returns a single joined string.

## Project

*Project CRUD, settings, import/export, database folders, archive/restore*

### `project_archive`

Archive a project to a .dra file.

The project must NOT be currently open.

Args:
    name: Exact name of the project to archive.
    file_path: Absolute destination path (should end in .dra).
    with_stills_and_luts: If True (default), include stills and LUTs
                          in the archive.

Returns:
    True if the archive succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `string` | *required* |  |
| `file_path` | `string` | *required* |  |
| `with_stills_and_luts` | `boolean` | `True` |  |

### `project_close`

Close the current project (saves automatically before closing).

Returns:
    True if the project was closed successfully.

### `project_create`

Create a new project and open it immediately.

Args:
    name: The name for the new project.  Must be unique within
          the current database folder.

Returns:
    The name of the created project.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `string` | *required* |  |

### `project_delete`

Delete a project by name.  The project must NOT be currently open.

Args:
    name: Exact name of the project to delete.  This action is
          irreversible.

Returns:
    True if the project was deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `string` | *required* |  |

### `project_export`

Export the current project to a .drp file.

Args:
    file_path: Absolute destination path (should end in .drp).
    with_stills_and_luts: If True (default), include stills and LUTs
                          in the exported file.  Set to False for a
                          smaller file without color assets.

Returns:
    True if the export succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `string` | *required* |  |
| `with_stills_and_luts` | `boolean` | `True` |  |

### `project_folder_create`

Create a new folder in the current database folder.

Args:
    folder_name: Name of the folder to create.

Returns:
    True if the folder was created.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_name` | `string` | *required* |  |

### `project_folder_delete`

Delete a folder from the current database folder.

The folder must be empty (no projects inside).

Args:
    folder_name: Name of the folder to delete.

Returns:
    True if the folder was deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_name` | `string` | *required* |  |

### `project_folder_goto_parent`

Navigate up one level in the project database folder hierarchy.

Returns:
    True if navigation succeeded. False if already at root.

### `project_folder_goto_root`

Navigate to the root of the project database.

Returns:
    True if navigation to root succeeded.

### `project_folder_list` `read-only`

List sub-folders in the current database folder.

Returns:
    A list of folder name strings.

### `project_folder_open`

Navigate into a sub-folder within the project database.

Args:
    folder_name: Name of the folder to open.

Returns:
    True if the folder was opened successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_name` | `string` | *required* |  |

### `project_get_current` `read-only`

Return basic info about the currently open project.

Returns:
    A dict with keys: name (str), timeline_count (int).

### `project_get_database` `read-only`

Return info about the current project database.

Returns:
    A dict with database info (DbType, DbName, IpAddress if remote).

### `project_get_database_list` `read-only`

List all available project databases.

Returns:
    A list of dicts, each with keys like "DbType", "DbName",
    and optionally "IpAddress" for remote databases.

### `project_get_setting` `read-only`

Read a single project setting by its key.

Args:
    key: The setting key, e.g. "timelineFrameRate",
         "timelineResolutionWidth".  See the Resolve Scripting API
         docs for the full list of valid keys.

Returns:
    The setting value as a string.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | `string` | *required* |  |

### `project_import`

Import a .drp project file into the current database folder.

Args:
    file_path: Absolute path to the .drp file to import.

Returns:
    True if the import succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `string` | *required* |  |

### `project_list` `read-only`

List all project names in the current database folder.

Returns an alphabetically-ordered list of project name strings.

### `project_open`

Open an existing project by name.

Args:
    name: Exact name of the project to open.  The current project
          will be closed automatically (and saved first by Resolve).

Returns:
    True if the project was opened successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `string` | *required* |  |

### `project_restore_archive`

Restore a project from a .dra archive file.

Args:
    file_path: Absolute path to the .dra archive file.

Returns:
    True if the restore succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `string` | *required* |  |

### `project_save`

Save the current project.

Returns:
    True if the save succeeded.

### `project_set_setting`

Write a project setting.

Args:
    key: The setting key (e.g. "timelineFrameRate").
    value: The new value as a string (e.g. "24").

Returns:
    True if the setting was applied successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | `string` | *required* |  |
| `value` | `string` | *required* |  |

## Media Storage

*Browse volumes, list files, import to media pool*

### `storage_get_files` `read-only`

List media files in a storage folder.

Args:
    folder_path: Absolute path to the folder to scan
                 (e.g. '/Volumes/Media/Projects/Footage').

Returns file paths found in the folder.  Resolve filters for
recognised media formats automatically.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_path` | `string` | *required* |  |

### `storage_get_subfolders` `read-only`

List subfolders inside a media storage path.

Args:
    volume_path: Absolute path to a mounted volume or subfolder
                 (e.g. '/Volumes/Media/Projects').

Returns a flat list of subfolder paths one level deep.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `volume_path` | `string` | *required* |  |

### `storage_get_volumes` `read-only`

List all mounted media storage volumes visible to DaVinci Resolve.

Returns the volume paths (e.g. '/' on macOS, 'C:\' on Windows, or
NAS mount points) that appear in the Media page's storage panel.

### `storage_import_to_pool`

Import files from media storage into the current project's media pool.

Args:
    file_paths: List of absolute file paths to import
                (e.g. ['/Volumes/Media/clip01.mov', '/Volumes/Media/clip02.mov']).

Returns the names of clips that were successfully imported.  An empty
list means nothing was imported (bad paths or unsupported formats).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_paths` | `list[string]` | *required* |  |

## Media Pool

*Folder CRUD, clip management, timeline creation, metadata*

### `media_pool_create_folder`

Create a new subfolder inside the current Media Pool folder.

Args:
    name: Name for the new subfolder.

Returns True if the folder was created.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `string` | *required* |  |

### `media_pool_create_timeline`

Create a new empty timeline in the current Media Pool folder.

Args:
    name: Name for the new timeline.

Returns the name of the created timeline.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `string` | *required* |  |

### `media_pool_create_timeline_from_clips`

Create a new timeline populated with specific clips from the current folder.

Args:
    name:       Name for the new timeline.
    clip_names: Ordered list of clip names to include.  Clips are
                searched in the current Media Pool folder.

Returns the name of the created timeline.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `string` | *required* |  |
| `clip_names` | `list[string]` | *required* |  |

### `media_pool_delete_clips`

Delete clips from the current Media Pool folder by name.

Args:
    clip_names: Names of clips to delete.

Returns True if the operation succeeded.  Clips not found are
silently skipped.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_names` | `list[string]` | *required* |  |

### `media_pool_delete_folders`

Delete Media Pool subfolders by name.

Args:
    folder_names: List of folder names to delete (searched in the
                  current folder's children).

Returns True if the operation succeeded.  Folders that are not found
are silently skipped.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_names` | `list[string]` | *required* |  |

### `media_pool_export_metadata`

Export metadata of all clips in the current folder to a CSV file.

Args:
    file_path: Absolute path for the output CSV file
               (e.g. '/Users/me/Desktop/metadata.csv').

Returns True if the export succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `string` | *required* |  |

### `media_pool_get_clips` `read-only`

List clips in the current Media Pool folder with pagination.

Args:
    offset: Number of clips to skip (default 0).
    limit:  Maximum clips to return per page (default 50).

Returns a dict with keys: items, total, offset, limit, has_more.
Each item contains: name, clip_color, duration, fps, resolution.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `offset` | `integer` | `0` |  |
| `limit` | `integer` | `50` |  |

### `media_pool_get_current_folder` `read-only`

Get the name of the currently selected Media Pool folder.

### `media_pool_get_root_folder` `read-only`

Get the name of the Media Pool's root folder.

Every project has exactly one root folder (usually named 'Master').

### `media_pool_get_subfolders` `read-only`

List the names of all subfolders in the current Media Pool folder.

### `media_pool_import_media`

Import media files from disk into the current Media Pool folder.

Args:
    file_paths: Absolute paths to media files to import.

Returns the names of successfully imported clips.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_paths` | `list[string]` | *required* |  |

### `media_pool_move_clips`

Move clips from the current folder to a different Media Pool folder.

Args:
    clip_names:         Names of clips to move.
    target_folder_name: Name of the destination folder (searched in
                        the current folder's siblings and root children).

Returns True if the clips were moved successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_names` | `list[string]` | *required* |  |
| `target_folder_name` | `string` | *required* |  |

### `media_pool_relink_clips`

Relink offline clips to media files in a new folder.

Args:
    clip_names:      Names of clips to relink.
    new_folder_path: Absolute path to the folder containing the
                     replacement media files.  Resolve matches by
                     filename within this folder.

Returns True if relinking succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_names` | `list[string]` | *required* |  |
| `new_folder_path` | `string` | *required* |  |

### `media_pool_set_current_folder`

Navigate into a Media Pool folder by name.

Args:
    folder_name: Exact name of the target folder.

Searches the immediate children of both the current folder and the root
folder.  Returns True if navigation succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_name` | `string` | *required* |  |

## Clips (Media Pool Item)

*Clip metadata, properties, colors, markers, flags, proxy, transcription*

### `clip_add_flag`

Add a flag of the given color to a clip.

Args:
    clip_name: Name of the clip.
    color:     Flag color (e.g. "Blue", "Red", "Green").

Returns:
    True if the flag was added.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |
| `color` | `string` | *required* |  |

### `clip_add_marker`

Add a marker to a media-pool clip at a given frame.

Args:
    clip_name:   Name of the clip.
    frame_id:    Frame number (relative to clip start) for the marker.
    color:       Marker color (e.g. "Blue", "Red", "Green").
    name:        Optional short label for the marker.
    note:        Optional longer note attached to the marker.
    duration:    Marker duration in frames (default 1).
    custom_data: Optional custom-data string stored with the marker.

Returns:
    True if the marker was added.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |
| `frame_id` | `integer` | *required* |  |
| `color` | `string` | *required* |  |
| `name` | `string` | `''` |  |
| `note` | `string` | `''` |  |
| `duration` | `integer` | `1` |  |
| `custom_data` | `string` | `''` |  |

### `clip_clear_color`

Remove the label color from a clip, resetting it to the default.

Args:
    clip_name: Name of the clip.

Returns:
    True if the color was cleared.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

### `clip_clear_flags`

Remove a specific flag color from a clip.

Args:
    clip_name: Name of the clip.
    color:     Flag color to remove (e.g. "Blue").

Returns:
    True if the flag was removed.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |
| `color` | `string` | *required* |  |

### `clip_clear_transcript`

Clear the transcript text from a clip.

Args:
    clip_name: Name of the clip.

Returns:
    True if the transcript was cleared.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

### `clip_delete_marker`

Delete the marker at a specific frame on a clip.

Args:
    clip_name: Name of the clip.
    frame_id:  Frame number of the marker to remove.

Returns:
    True if the marker was deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |
| `frame_id` | `integer` | *required* |  |

### `clip_get_color` `read-only`

Return the label color assigned to a clip (e.g. "Orange", "Blue").

Args:
    clip_name: Name of the clip.

Returns:
    Color name string, or empty string if no color is set.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

### `clip_get_flags` `read-only`

Return all flag colors currently set on a clip.

Args:
    clip_name: Name of the clip.

Returns:
    List of color name strings (e.g. ["Blue", "Red"]).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

### `clip_get_markers` `read-only`

Return all markers on a clip. Keys are frame IDs (as strings).

Args:
    clip_name: Name of the clip.

Returns:
    Dict mapping frame ID to marker info dict with keys:
    color, name, note, duration, customData.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

### `clip_get_metadata` `read-only`

Return all metadata fields for a clip as key-value pairs.

Args:
    clip_name: Name of the clip to inspect.

Returns:
    Dict of metadata keys and their string values.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

### `clip_get_name` `read-only`

Return the display name of a media-pool clip.

Args:
    clip_name: Current name of the clip to look up.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

### `clip_get_properties` `read-only`

Return all clip properties (Clip Name, Duration, FPS, etc.).

Args:
    clip_name: Name of the clip to inspect.

Returns:
    Dict with property keys like "Clip Name", "Duration", "FPS",
    "Start TC", "End TC", "File Path", etc.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

### `clip_get_transcript` `read-only`

Get the transcript text for a clip.

Args:
    clip_name: Name of the clip.

Returns:
    The transcript text string, or empty string if not transcribed.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

### `clip_link_proxy`

Link an external proxy media file to a clip.

Args:
    clip_name:  Name of the clip.
    proxy_path: Absolute file-system path to the proxy media file.

Returns:
    True if the proxy was linked successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |
| `proxy_path` | `string` | *required* |  |

### `clip_replace`

Replace a clip's media file with a new file.

Args:
    clip_name:     Name of the clip whose media to replace.
    new_file_path: Absolute file-system path to the replacement media file.

Returns:
    True if the replacement succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |
| `new_file_path` | `string` | *required* |  |

### `clip_set_color`

Set the label color on a clip.

Args:
    clip_name: Name of the clip.
    color:     Color name (e.g. "Orange", "Apricot", "Yellow",
               "Lime", "Olive", "Green", "Teal", "Navy", "Blue",
               "Purple", "Violet", "Pink", "Tan", "Beige",
               "Brown", "Chocolate").

Returns:
    True if the color was applied.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |
| `color` | `string` | *required* |  |

### `clip_set_metadata`

Set a single metadata field on a clip.

Args:
    clip_name: Name of the clip to modify.
    key:       Metadata field name (e.g. "Description", "Comments").
    value:     Value to assign.

Returns:
    True if the metadata was set successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |
| `key` | `string` | *required* |  |
| `value` | `string` | *required* |  |

### `clip_set_name`

Rename a media-pool clip.

Args:
    clip_name: Current name of the clip.
    new_name:  Desired new display name.

Returns:
    True if the rename succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |
| `new_name` | `string` | *required* |  |

### `clip_set_property`

Set a single property on a clip.

Args:
    clip_name: Name of the clip to modify.
    key:       Property key (e.g. "Clip Name", "Start TC").
    value:     Value to assign as a string.

Returns:
    True if the property was set successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |
| `key` | `string` | *required* |  |
| `value` | `string` | *required* |  |

### `clip_transcribe_audio`

Start audio transcription for a clip.

Requires DaVinci Resolve 19+ with speech-to-text support enabled.

Args:
    clip_name: Name of the clip to transcribe.

Returns:
    True if transcription was initiated.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

### `clip_unlink_proxy`

Remove proxy media link from a clip.

Args:
    clip_name: Name of the clip whose proxy link to remove.

Returns:
    True if the proxy was unlinked successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_name` | `string` | *required* |  |

## Timeline

*Timeline CRUD, tracks, items, markers, export, compound/Fusion clips, settings*

### `timeline_add_marker`

Add a marker to the current timeline at a specific frame.

Args:
    frame_id: Frame number where the marker should be placed.
    color: Marker color.  Standard Resolve colors include "Blue",
           "Cyan", "Green", "Yellow", "Red", "Pink", "Purple",
           "Fuchsia", "Rose", "Lavender", "Sky", "Mint", "Lemon",
           "Sand", "Cocoa", "Cream".
    name: Optional marker name/title.
    note: Optional marker note/description.
    duration: Marker duration in frames (default 1).
    custom_data: Optional custom data string for the marker.

Returns:
    True if the marker was added.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frame_id` | `integer` | *required* |  |
| `color` | `string` | *required* |  |
| `name` | `string` | `''` |  |
| `note` | `string` | `''` |  |
| `duration` | `integer` | `1` |  |
| `custom_data` | `string` | `''` |  |

### `timeline_add_track`

Add one or more tracks to the current timeline.

Args:
    track_type: Type of track to add: "video", "audio", or "subtitle".
    count: Number of tracks to add (default 1).  Each call to the
           Resolve API adds a single track, so this repeats the call.

Returns:
    True if all requested tracks were added successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_type` | `string` | *required* |  |
| `count` | `integer` | `1` |  |

### `timeline_append_clips`

Append media pool clips to the end of the current timeline.

Searches the media pool's current folder for clips matching the
given names, then appends them in order.

Args:
    clip_names: List of clip names (as shown in the media pool)
                to append to the timeline.

Returns:
    True if the clips were appended successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `clip_names` | `list[string]` | *required* |  |

### `timeline_create_compound_clip`

Create a compound clip from timeline items on a specific track.

A compound clip merges multiple timeline items into one editable unit.

Args:
    item_names: Names of timeline items to combine.
    track_type: Track type to search for items ("video", "audio",
        "subtitle"). Defaults to "video".
    track_index: 1-based track index. Defaults to 1.
    clip_name: Optional name for the compound clip. If empty,
        Resolve generates a default name.

Returns:
    True if the compound clip was created.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_names` | `list[string]` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |
| `clip_name` | `string` | `''` |  |

### `timeline_create_fusion_clip`

Create a Fusion clip from timeline items on a specific track.

A Fusion clip wraps selected items into a single Fusion composition
that can be opened and edited in the Fusion page.

Args:
    item_names: Names of timeline items to combine.
    track_type: Track type to search ("video", "audio", "subtitle").
        Defaults to "video".
    track_index: 1-based track index. Defaults to 1.

Returns:
    True if the Fusion clip was created.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_names` | `list[string]` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `timeline_create_subtitles_from_audio`

Auto-generate subtitles from audio in the current timeline.

Uses Resolve's built-in speech-to-text to create subtitle track
items.  Requires DaVinci Resolve 18.5 or later.

Returns:
    True if subtitles were generated successfully.

### `timeline_delete_clips`

Delete timeline items by name from a specific track.

Args:
    item_names: Names of the timeline items to delete.
    track_type: Type of track to search: "video", "audio", or "subtitle".
                Defaults to "video".
    track_index: 1-based index of the track to search (default 1).

Returns:
    True if the items were deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_names` | `list[string]` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `timeline_delete_marker`

Delete a marker at a specific frame on the current timeline.

Args:
    frame_id: Frame number of the marker to delete.

Returns:
    True if the marker was deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frame_id` | `integer` | *required* |  |

### `timeline_delete_track`

Delete a track from the current timeline.

Args:
    track_type: Type of track: "video", "audio", or "subtitle".
    track_index: 1-based index of the track to delete.

Returns:
    True if the track was deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_type` | `string` | *required* |  |
| `track_index` | `integer` | *required* |  |

### `timeline_detect_scene_cuts` `read-only`

Detect scene cuts in the current timeline.

Analyzes the video content and returns frame numbers where scene
transitions were detected.  Requires DaVinci Resolve 18.5 or later.

Returns:
    A list of frame numbers where cuts were detected.

### `timeline_duplicate`

Duplicate the current timeline.

Returns:
    The name of the newly created timeline, or None if duplication
    failed.

### `timeline_export`

Export the current timeline to a file (AAF, EDL, FCPXML, etc.).

Args:
    file_path: Absolute destination path for the exported file.
    export_type: Format to export. One of: "AAF", "DRT", "EDL",
        "FCPXML", "HDR10 Profile A", "HDR10 Profile B", "OTIO",
        "Text CSV", "Text Tab". Defaults to "AAF".
    export_subtype: Sub-type for EDL exports. One of: "" (none),
        "SMPTE", "Avid", "CMX 3600". Defaults to "".

Returns:
    True if the export succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `string` | *required* |  |
| `export_type` | `string` | `'AAF'` |  |
| `export_subtype` | `string` | `''` |  |

### `timeline_get_by_index` `read-only`

Return info about a timeline at the given 1-based index.

Args:
    index: 1-based position of the timeline in the project.

Returns:
    A dict with keys: name, start_frame, end_frame,
    video_tracks, audio_tracks, start_timecode.
    None if no timeline exists at the given index.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `index` | `integer` | *required* |  |

### `timeline_get_count` `read-only`

Return the number of timelines in the current project.

### `timeline_get_current` `read-only`

Return info about the current timeline, or None if no timeline is open.

Returns a dict with keys: name, start_frame, end_frame,
video_tracks, audio_tracks, start_timecode.

### `timeline_get_end_frame` `read-only`

Return the end frame number of the current timeline.

### `timeline_get_items_in_track` `read-only`

List timeline items on a specific track with pagination.

Args:
    track_type: One of "video", "audio", or "subtitle".
    track_index: 1-based index of the track.
    offset: Number of items to skip from the start (default 0).
    limit: Maximum number of items to return (default 50).

Returns:
    A dict with keys: items (list of {name, start, end, duration}),
    total, offset, limit, has_more.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_type` | `string` | *required* |  |
| `track_index` | `integer` | *required* |  |
| `offset` | `integer` | `0` |  |
| `limit` | `integer` | `50` |  |

### `timeline_get_markers` `read-only`

Return all markers on the current timeline.

Returns:
    A dict mapping frame numbers (as string keys) to marker info dicts.
    Each marker dict contains: color, duration, note, name, customData.
    Returns an empty dict if no markers exist or no timeline is open.

### `timeline_get_name` `read-only`

Return the name of the current timeline.

Raises an error if no timeline is open.

### `timeline_get_setting` `read-only`

Read a timeline-specific setting by key.

Args:
    key: The setting key name (e.g. "timelineFrameRate",
        "timelineResolutionWidth", "timelineResolutionHeight").

Returns:
    The setting value as a string.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | `string` | *required* |  |

### `timeline_get_start_frame` `read-only`

Return the start frame number of the current timeline.

### `timeline_get_track_count` `read-only`

Return the number of tracks of the given type in the current timeline.

Args:
    track_type: One of "video", "audio", or "subtitle".
                Defaults to "video".

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_type` | `string` | `'video'` |  |

### `timeline_get_track_name` `read-only`

Return the name of a specific track in the current timeline.

Args:
    track_type: One of "video", "audio", or "subtitle".
    track_index: 1-based index of the track.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_type` | `string` | *required* |  |
| `track_index` | `integer` | *required* |  |

### `timeline_set_current`

Set the current timeline by name.

Args:
    name: Exact name of the timeline to activate.  Searches all
          timelines in the current project by index.

Returns:
    True if the timeline was found and set as current.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `string` | *required* |  |

### `timeline_set_name`

Rename the current timeline.

Args:
    name: The new name for the current timeline.

Returns:
    True if the rename succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `string` | *required* |  |

### `timeline_set_setting`

Write a timeline-specific setting.

Args:
    key: The setting key name (e.g. "timelineFrameRate",
        "timelineResolutionWidth", "timelineResolutionHeight").
    value: The value to set (as a string).

Returns:
    True if the setting was applied.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | `string` | *required* |  |
| `value` | `string` | *required* |  |

### `timeline_set_track_enabled`

Enable or disable a track in the current timeline.

Args:
    track_type: One of "video", "audio", or "subtitle".
    track_index: 1-based index of the track.
    enabled: True to enable, False to disable the track.

Returns:
    True if the operation succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_type` | `string` | *required* |  |
| `track_index` | `integer` | *required* |  |
| `enabled` | `boolean` | *required* |  |

### `timeline_set_track_locked`

Lock or unlock a track in the current timeline.

Args:
    track_type: One of "video", "audio", or "subtitle".
    track_index: 1-based index of the track.
    locked: True to lock the track, False to unlock it.

Returns:
    True if the operation succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_type` | `string` | *required* |  |
| `track_index` | `integer` | *required* |  |
| `locked` | `boolean` | *required* |  |

### `timeline_set_track_name`

Rename a track in the current timeline.

Args:
    track_type: One of "video", "audio", or "subtitle".
    track_index: 1-based index of the track.
    name: The new display name for the track.

Returns:
    True if the rename succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `track_type` | `string` | *required* |  |
| `track_index` | `integer` | *required* |  |
| `name` | `string` | *required* |  |

## Timeline Items

*Transform, crop, composite, color labels, markers, flags, takes, stabilize*

### `item_add_flag`

Add a flag of the given color to a timeline item.

Args:
    item_name:   Name of the item.
    color:       Flag color (e.g. "Blue", "Red", "Green").
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the flag was added.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `color` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_add_marker`

Add a marker to a timeline item at a given frame offset.

Args:
    item_name:   Name of the item.
    frame_id:    Frame offset from the item's start for the marker.
    color:       Marker color (e.g. "Blue", "Red", "Green").
    name:        Optional short label for the marker.
    note:        Optional longer note attached to the marker.
    duration:    Marker duration in frames (default 1).
    custom_data: Optional custom-data string stored with the marker.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the marker was added.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `frame_id` | `integer` | *required* |  |
| `color` | `string` | *required* |  |
| `name` | `string` | `''` |  |
| `note` | `string` | `''` |  |
| `duration` | `integer` | `1` |  |
| `custom_data` | `string` | `''` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_add_node`

Add a color correction node to the timeline item's node graph.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if a new node was added.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_delete_marker`

Delete the marker at a specific frame offset on a timeline item.

Args:
    item_name:   Name of the item.
    frame_id:    Frame offset of the marker to remove.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the marker was deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `frame_id` | `integer` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_delete_take_by_index`

Delete a take at the given index on a timeline item.

Args:
    item_name:   Name of the item.
    take_index:  1-based index of the take to delete.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the take was deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `take_index` | `integer` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_finalize_take`

Finalize the current take on a timeline item.

This commits the current take, removing other take options.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the take was finalized.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_color` `read-only`

Return the label color assigned to a timeline item.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    Color name string, or empty string if none is set.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_duration` `read-only`

Return the duration of a timeline item in frames.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_flags` `read-only`

Return all flag colors currently set on a timeline item.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    List of color name strings (e.g. ["Blue", "Red"]).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_linked_items` `read-only`

Return items linked to this timeline item (e.g. audio for a video clip).

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    List of dicts, each with a "name" key. Empty list if no linked items.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_markers` `read-only`

Return all markers on a timeline item. Keys are frame offsets.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    Dict mapping frame offset to marker info dict with keys:
    color, name, note, duration, customData.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_media_pool_item` `read-only`

Return the source media-pool clip for a timeline item, if available.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    Dict with "name" and "file_path" keys, or None if no source clip
    is linked (e.g. for generators or titles).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_name` `read-only`

Return the display name of a timeline item.

Args:
    item_name:   Name of the item to look up.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_properties` `read-only`

Return all properties of a timeline item as key-value pairs.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    Dict of property keys and values (e.g. "ZoomX", "Pan", "Opacity").

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_start_end` `read-only`

Return the start frame, end frame, and duration of a timeline item.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    Dict with keys: start, end, duration (all integers in frames).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_take_by_index` `read-only`

Return info about a take at the given 1-based index.

Args:
    item_name:   Name of the item.
    take_index:  1-based index of the take.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    A dict with take info, or None if the index is invalid.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `take_index` | `integer` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_takes_count` `read-only`

Return the number of takes on a timeline item.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    Number of takes available for the item.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_get_unique_id` `read-only`

Return the unique identifier for a timeline item.

This ID is stable across project saves and can be used to
reference a specific item programmatically.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    Unique ID string for the item.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_select_take_by_index`

Select a specific take on a timeline item.

Args:
    item_name:   Name of the item.
    take_index:  1-based index of the take to select.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the take was selected.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `take_index` | `integer` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_set_color`

Set the label color on a timeline item.

Args:
    item_name:   Name of the item.
    color:       Color name (e.g. "Orange", "Blue", "Green").
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the color was applied.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `color` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_set_composite`

Set composite mode and/or opacity on a timeline item.

Args:
    item_name:   Name of the item.
    mode:        Composite/blend mode name (e.g. "Normal", "Add",
                 "Multiply", "Screen", "Overlay").
    opacity:     Opacity value from 0 (transparent) to 100 (opaque).
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the composite settings were applied.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `mode` | `string` | `None` |  |
| `opacity` | `number` | `None` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_set_crop`

Set crop values on a timeline item.

Only non-None parameters are applied; the rest remain unchanged.

Args:
    item_name:   Name of the item.
    left:        Left crop value.
    right:       Right crop value.
    top:         Top crop value.
    bottom:      Bottom crop value.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if all provided crop values were applied.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `left` | `number` | `None` |  |
| `right` | `number` | `None` |  |
| `top` | `number` | `None` |  |
| `bottom` | `number` | `None` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_set_enabled`

Enable or disable a timeline item (muted/unmuted).

Args:
    item_name:   Name of the item.
    enabled:     True to enable, False to disable (mute).
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the state was changed.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `enabled` | `boolean` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_set_property`

Set a single property on a timeline item.

Args:
    item_name:   Name of the item.
    key:         Property key (e.g. "ZoomX", "Pan", "Opacity").
    value:       Value to assign as a string.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the property was set successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `key` | `string` | *required* |  |
| `value` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_set_transform`

Set transform properties (zoom, position, rotation, anchor) on an item.

Only non-None parameters are applied; the rest remain unchanged.

Args:
    item_name:   Name of the item.
    zoom_x:      Horizontal zoom factor (1.0 = 100%).
    zoom_y:      Vertical zoom factor (1.0 = 100%).
    position_x:  Horizontal pan offset in pixels.
    position_y:  Vertical tilt offset in pixels.
    rotation:    Rotation angle in degrees.
    anchor_x:    Anchor point X coordinate.
    anchor_y:    Anchor point Y coordinate.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if all provided transforms were applied.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `zoom_x` | `number` | `None` |  |
| `zoom_y` | `number` | `None` |  |
| `position_x` | `number` | `None` |  |
| `position_y` | `number` | `None` |  |
| `rotation` | `number` | `None` |  |
| `anchor_x` | `number` | `None` |  |
| `anchor_y` | `number` | `None` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_smart_reframe`

Apply smart reframe to a timeline item.

Args:
    item_name:          Name of the item.
    target_ratio:       Target aspect ratio string (e.g. "9:16", "1:1").
    motion_estimation:  Quality of motion estimation — one of
                        "faster", "normal", or "better".
    track_type:         Track type — "video" or "audio".
    track_index:        1-based track number.

Returns:
    True if the smart reframe was applied successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `target_ratio` | `string` | `'9:16'` |  |
| `motion_estimation` | `string` | `'normal'` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `item_stabilize`

Run stabilization analysis on a timeline item.

Args:
    item_name:   Name of the item.
    track_type:  Track type — "video" or "audio".
    track_index: 1-based track number.

Returns:
    True if the stabilization analysis completed successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

## Render

*Formats, codecs, presets, job queue, rendering, progress*

### `render_add_job`

Add the current timeline to the render queue with current settings.

The timeline must be set (Deliver page) and render settings must be
configured before calling this tool.

Returns:
    The job ID string for the newly queued render job.

### `render_delete_all_jobs`

Delete all render jobs from the queue.

Returns:
    True if all jobs were deleted successfully.

### `render_delete_job`

Delete a specific render job from the queue.

Args:
    job_id: The job ID string returned by render_add_job() or
            found in render_get_jobs() results.

Returns:
    True if the job was deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `job_id` | `string` | *required* |  |

### `render_get_codecs` `read-only`

Return available codecs for a given render format.

Args:
    format_name: The render format name (e.g. "QuickTime", "mp4").
                 Get valid names from render_get_formats().

Returns:
    A dict of {codecName: description} for the specified format.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format_name` | `string` | *required* |  |

### `render_get_format_and_codec` `read-only`

Return the currently selected render format and codec.

Returns:
    A dict with keys "format" and "codec" (both strings).

### `render_get_formats` `read-only`

Return available render formats as {formatName: description}.

Use the format names as input for render_get_codecs() or
render_set_format_and_codec().

### `render_get_jobs` `read-only`

Return all render jobs in the queue with their current status.

Returns:
    A list of dicts, each with keys: job_id, status, timeline_name,
    target_dir, output_filename.

### `render_get_presets` `read-only`

List all saved render preset names.

Returns:
    A list of preset name strings that can be passed to
    render_load_preset().

### `render_get_status` `read-only`

Return the render progress for a specific job.

Args:
    job_id: The job ID to check.

Returns:
    A dict with keys: job_id (str), status (str),
    progress (int, 0-100), time_remaining (int, milliseconds).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `job_id` | `string` | *required* |  |

### `render_load_preset`

Load a render preset by name, applying its settings.

Args:
    preset_name: Exact name of the preset.  Get valid names from
                 render_get_presets().

Returns:
    True if the preset was loaded successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `preset_name` | `string` | *required* |  |

### `render_set_format_and_codec`

Set the render format and codec.

Args:
    format_name: The format name (e.g. "QuickTime").
    codec_name: The codec name within that format (e.g. "H.265").
                Get valid combinations from render_get_formats() and
                render_get_codecs().

Returns:
    True if the format and codec were set successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format_name` | `string` | *required* |  |
| `codec_name` | `string` | *required* |  |

### `render_set_settings`

Apply render settings from a dictionary.

Args:
    settings: A dict of render setting key-value pairs.  Valid keys:
              TargetDir, CustomName, FormatWidth, FormatHeight,
              FrameRate, MarkIn, MarkOut, AudioCodec, AudioBitDepth,
              AudioSampleRate, ExportAlpha.

Returns:
    True if all settings were applied successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `settings` | `dict` | *required* |  |

### `render_start`

Start rendering queued jobs.

Args:
    job_ids: Optional list of specific job IDs to render.  If None,
             all queued jobs are rendered.
    is_interactive: If True, rendering will show the visual preview
                    in Resolve (slower but useful for monitoring).

Returns:
    True if rendering started successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `job_ids` | `array` | `None` |  |
| `is_interactive` | `boolean` | `False` |  |

### `render_stop`

Stop the currently running render.

Returns:
    True if rendering was stopped.  Also returns True if no render
    was in progress (idempotent).

## Color

*Nodes, LUTs, CDL, grade versions, DRX, color groups, node labels*

### `color_add_version`

Create a new local grade version on a timeline item.

Args:
    item_name:    Exact name of the timeline clip.
    version_name: Name for the new grade version.
    track_type:   Track type (default "video").
    track_index:  1-based track number (default 1).

Returns:
    True if the version was created.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `version_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_apply_drx`

Apply a DaVinci Resolve grade preset (.drx) to one or more items.

Args:
    drx_path:    Absolute file path to the .drx grade file.
    grade_mode:  Grade mode: 0 = No keyframes, 1 = Source, 2 = Timeline.
    item_names:  List of timeline clip names to receive the grade.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the grade was applied to all items successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `drx_path` | `string` | *required* |  |
| `grade_mode` | `integer` | *required* |  |
| `item_names` | `list[string]` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_assign_to_group`

Assign a timeline item to a color group.

Args:
    item_name:   Exact name of the timeline clip.
    group_id:    ID of the target color group (from color_get_group_list).
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the item was assigned.  Returns False if the API
    is not supported in the current Resolve version.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `group_id` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_create_group`

Create a new color group in the current project.

Args:
    group_name: Name for the new color group.

Returns:
    True if the group was created.  Returns False if the API
    is not supported in the current Resolve version.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group_name` | `string` | *required* |  |

### `color_delete_group`

Delete a color group from the current project by its ID.

Args:
    group_id: The unique identifier of the color group to delete.
              Obtain IDs from color_get_group_list().

Returns:
    True if the group was deleted.  Returns False if the API
    is not supported in the current Resolve version.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `group_id` | `string` | *required* |  |

### `color_delete_version`

Delete a grade version from a timeline item.

Args:
    item_name:    Exact name of the timeline clip.
    version_name: Name of the version to delete.
    version_type: 0 for local (default), 1 for remote.
    track_type:   Track type (default "video").
    track_index:  1-based track number (default 1).

Returns:
    True if the version was deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `version_name` | `string` | *required* |  |
| `version_type` | `integer` | `0` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_export_lut`

Export the combined grade of a timeline item as a LUT file.

Args:
    item_name:   Exact name of the timeline clip.
    lut_type:    LUT format string, e.g. "3D LUT (33 Point)", "3D LUT (65 Point)".
    export_path: Absolute destination file path for the exported LUT.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the LUT was exported successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `lut_type` | `string` | *required* |  |
| `export_path` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_get_cdl` `read-only`

Read the ASC CDL values from a timeline item's current node.

Args:
    item_name:   Exact name of the timeline clip.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    A dict with keys: Slope ([R,G,B]), Offset ([R,G,B]),
    Power ([R,G,B]), Saturation (float).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_get_current_version` `read-only`

Return the name of the currently active grade version.

Args:
    item_name:    Exact name of the timeline clip.
    version_type: 0 for local (default), 1 for remote.
    track_type:   Track type (default "video").
    track_index:  1-based track number (default 1).

Returns:
    The active version name, or "" if unavailable.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `version_type` | `integer` | `0` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_get_group_list` `read-only`

List all color groups defined in the current project.

Returns:
    A list of dicts, each with at least "name" and "id" keys.
    Returns an empty list if the API is not supported or no
    groups are defined.

### `color_get_lut` `read-only`

Return the LUT file path applied to a specific node, or empty string.

Args:
    item_name:   Exact name of the timeline clip.
    node_index:  1-based index of the node to query.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    The absolute path to the applied LUT, or "" if none is set.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `node_index` | `integer` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_get_node_label` `read-only`

Get the label of a specific color correction node.

Args:
    item_name:   Exact name of the timeline clip.
    node_index:  1-based index of the node to query.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    The label string for the node, or "" if none is set.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `node_index` | `integer` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_get_num_nodes` `read-only`

Return the number of color correction nodes on a timeline item.

Args:
    item_name:   Exact name of the timeline clip.
    track_type:  Track type — "video" or "audio" (default "video").
    track_index: 1-based track number (default 1).

Returns:
    The node count as an integer.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_get_version_count` `read-only`

Return the number of grade versions on a timeline item.

Args:
    item_name:    Exact name of the timeline clip.
    version_type: 0 for local versions, 1 for remote versions.
    track_type:   Track type (default "video").
    track_index:  1-based track number (default 1).

Returns:
    The version count as an integer.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `version_type` | `integer` | `0` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_get_versions` `read-only`

List all grade version names on a timeline item.

Args:
    item_name:    Exact name of the timeline clip.
    version_type: 0 for local versions (default), 1 for remote versions.
    track_type:   Track type (default "video").
    track_index:  1-based track number (default 1).

Returns:
    A list of version name strings.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `version_type` | `integer` | `0` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_load_version`

Load a specific grade version onto a timeline item, replacing current.

Unlike set_current_version (which switches), load_version replaces
the current grade data with the contents of the named version.

Args:
    item_name:    Exact name of the timeline clip.
    version_name: Name of the version to load.
    version_type: 0 for local (default), 1 for remote.
    track_type:   Track type (default "video").
    track_index:  1-based track number (default 1).

Returns:
    True if the version was loaded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `version_name` | `string` | *required* |  |
| `version_type` | `integer` | `0` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_remove_from_group`

Remove a timeline item from a color group.

Args:
    item_name:   Exact name of the timeline clip.
    group_id:    ID of the color group to leave (from color_get_group_list).
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the item was removed.  Returns False if the API
    is not supported in the current Resolve version.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `group_id` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_rename_version`

Rename a grade version on a timeline item.

Args:
    item_name:    Exact name of the timeline clip.
    old_name:     Current name of the version.
    new_name:     Desired new name for the version.
    version_type: 0 for local (default), 1 for remote.
    track_type:   Track type (default "video").
    track_index:  1-based track number (default 1).

Returns:
    True if the version was renamed.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `old_name` | `string` | *required* |  |
| `new_name` | `string` | *required* |  |
| `version_type` | `integer` | `0` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_reset_grade`

Reset a timeline item's grade to identity (neutral) CDL values.

Sets Slope=[1,1,1], Offset=[0,0,0], Power=[1,1,1], Saturation=1.0.
This effectively neutralises the grade without removing nodes.

Args:
    item_name:   Exact name of the timeline clip.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the reset succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_set_cdl`

Set ASC CDL values on a timeline item's current node.

Args:
    item_name:   Exact name of the timeline clip.
    cdl:         CDL dictionary with keys:
                 - "Slope": [R, G, B] floats (default [1,1,1])
                 - "Offset": [R, G, B] floats (default [0,0,0])
                 - "Power": [R, G, B] floats (default [1,1,1])
                 - "Saturation": float (default 1.0)
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the CDL values were applied successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `cdl` | `dict` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_set_current_version`

Switch to a specific grade version on a timeline item.

Args:
    item_name:    Exact name of the timeline clip.
    version_name: Name of the version to activate.
    version_type: 0 for local (default), 1 for remote.
    track_type:   Track type (default "video").
    track_index:  1-based track number (default 1).

Returns:
    True if the version was activated.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `version_name` | `string` | *required* |  |
| `version_type` | `integer` | `0` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_set_lut`

Apply a LUT file to a specific node on a timeline item.

Args:
    item_name:   Exact name of the timeline clip.
    node_index:  1-based index of the target node.
    lut_path:    Absolute file path to the .cube / .3dl LUT file.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the LUT was applied successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `node_index` | `integer` | *required* |  |
| `lut_path` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_set_node_enabled`

Enable or disable a specific color correction node.

Args:
    item_name:   Exact name of the timeline clip.
    node_index:  1-based index of the node to toggle.
    enabled:     True to enable, False to disable.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the operation succeeded.  Returns False if the Resolve
    scripting API does not support per-node enable/disable in the
    current version.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `node_index` | `integer` | *required* |  |
| `enabled` | `boolean` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `color_set_node_label`

Set the label on a specific color correction node.

Args:
    item_name:   Exact name of the timeline clip.
    node_index:  1-based index of the node to label.
    label:       Label string to assign to the node.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the label was set successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `node_index` | `integer` | *required* |  |
| `label` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

## Fusion

*Compositions CRUD, generators, titles, tool listing*

### `fusion_add_comp`

Add a new Fusion composition to the timeline item under the playhead.

This operates on the currently selected video item (the clip at the
playhead position).  Use playback tools to position the playhead first.

Returns:
    True if a new composition was added.

### `fusion_delete_comp`

Delete a Fusion composition from a timeline item by name.

Args:
    item_name:   Exact name of the timeline clip.
    comp_name:   Name of the Fusion composition to delete.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the composition was deleted.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `comp_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `fusion_export_comp`

Export a Fusion composition to a .comp file on disk.

Args:
    item_name:   Exact name of the timeline clip.
    comp_name:   Name of the Fusion composition to export.
    export_path: Absolute destination path (should end in .comp).
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the composition was exported successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `comp_name` | `string` | *required* |  |
| `export_path` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `fusion_get_comp` `read-only`

Return basic information about a Fusion composition by name.

Args:
    item_name:   Exact name of the timeline clip.
    comp_name:   Name of the Fusion composition to query.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    A dict with "name" and "tool_count" keys if the comp exists,
    or None if not found.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `comp_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `fusion_get_comp_count` `read-only`

Return the number of Fusion compositions on a timeline item.

Args:
    item_name:   Exact name of the timeline clip.
    track_type:  Track type — "video" or "audio" (default "video").
    track_index: 1-based track number (default 1).

Returns:
    The composition count as an integer.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `fusion_get_comp_names` `read-only`

List the names of all Fusion compositions on a timeline item.

Args:
    item_name:   Exact name of the timeline clip.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    A list of composition name strings.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `fusion_get_tool_list` `read-only`

List all Fusion tools inside a specific composition.

Args:
    item_name:   Exact name of the timeline clip.
    comp_name:   Name of the Fusion composition to inspect.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    A list of tool name strings (e.g. ["MediaIn1", "Transform1",
    "MediaOut1"]).  Returns an empty list if the comp has no tools
    or the API does not support tool listing.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `comp_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `fusion_import_comp`

Import a Fusion composition file (.comp) onto a timeline item.

Args:
    item_name:   Exact name of the timeline clip.
    comp_path:   Absolute path to the .comp file to import.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the composition was imported successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `comp_path` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `fusion_insert_generator`

Insert a Fusion generator into the current timeline.

The generator is appended at the end of the timeline via the
Media Pool's AppendToTimeline API with mediaType "generator".

Args:
    generator_name: Name of the Fusion generator to insert,
                    e.g. "Fusion Composition", "Text+".

Returns:
    True if the generator was inserted successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `generator_name` | `string` | *required* |  |

### `fusion_insert_title`

Insert a Fusion title into the current timeline.

The title is appended at the end of the timeline via the
Media Pool's AppendToTimeline API with mediaType "title".

Args:
    title_name: Name of the Fusion title template to insert,
                e.g. "Text+", "Scroll".

Returns:
    True if the title was inserted successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title_name` | `string` | *required* |  |

### `fusion_rename_comp`

Rename a Fusion composition on a timeline item.

Args:
    item_name:   Exact name of the timeline clip.
    old_name:    Current name of the Fusion composition.
    new_name:    Desired new name.
    track_type:  Track type (default "video").
    track_index: 1-based track number (default 1).

Returns:
    True if the composition was renamed.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `item_name` | `string` | *required* |  |
| `old_name` | `string` | *required* |  |
| `new_name` | `string` | *required* |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

## Gallery

*Still albums, grab/import/export stills, PowerGrades*

### `gallery_apply_grade_from_still`

Apply the color grade from a gallery still to timeline items.

Args:
    still_index:  Zero-based index of the still in the album (from
                  gallery_get_stills).
    item_names:   Names of timeline items to apply the grade to.
    album_name:   Source album.  Uses the current album if not specified.
    track_type:   Track type to search for items: "video" or "audio"
                  (default "video").
    track_index:  1-based track index to search for items (default 1).

Returns True if the grade was applied to at least one item.
The ApplyGradeFromGalleryStill API may not exist in all Resolve versions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `still_index` | `integer` | *required* |  |
| `item_names` | `list[string]` | *required* |  |
| `album_name` | `string` | `None` |  |
| `track_type` | `string` | `'video'` |  |
| `track_index` | `integer` | `1` |  |

### `gallery_create_album`

Create a new still album in the Gallery.

Args:
    name: Display name for the new album.

Returns True if the album was created.
This method may not be available in all Resolve versions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `string` | *required* |  |

### `gallery_delete_album`

Delete a still album from the Gallery.

Args:
    album_name: Name of the album to delete.

Returns True if the album was deleted.
This method may not be available in all Resolve versions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `album_name` | `string` | *required* |  |

### `gallery_delete_stills`

Delete stills from a Gallery album by index.

Args:
    still_indices: Zero-based indices of stills to delete (from
                   gallery_get_stills).
    album_name:    Target album name.  Uses the current album if
                   not specified.

Returns True if the deletion succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `still_indices` | `list[integer]` | *required* |  |
| `album_name` | `string` | `None` |  |

### `gallery_export_stills`

Export stills from a Gallery album to disk.

Args:
    still_indices: Zero-based indices of stills to export (from
                   gallery_get_stills).
    export_path:   Absolute path to the output directory.
    album_name:    Source album name.  Uses the current album if
                   not specified.

Returns True if the export succeeded.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `still_indices` | `list[integer]` | *required* |  |
| `export_path` | `string` | *required* |  |
| `album_name` | `string` | `None` |  |

### `gallery_get_albums` `read-only`

List the names of all still albums in the Gallery.

Returns album names as strings.  Requires an open project.

### `gallery_get_current_album` `read-only`

Return the name of the currently active still album.

Returns an empty string if no album is currently selected.

### `gallery_get_powergrade_albums` `read-only`

List the names of all PowerGrade albums in the Gallery.

PowerGrade albums contain grades that persist across projects.
This method may not be available in all Resolve versions.

### `gallery_get_powergrade_stills` `read-only`

List stills in a PowerGrade album.

Args:
    album_name: Name of the PowerGrade album.

Returns a list of dicts with "index" and "name" keys, similar
to gallery_get_stills.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `album_name` | `string` | *required* |  |

### `gallery_get_stills` `read-only`

List stills in a Gallery album.

Args:
    album_name: Name of the album to list.  Uses the current album
                if not specified.

Returns a list of dicts, each with a "name" key (the still's label
or a numeric index if no label is available) and an "index" key.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `album_name` | `string` | `None` |  |

### `gallery_grab_still`

Grab a still from the current viewer into the current album.

Captures a snapshot of whatever is currently displayed in the Resolve
viewer and adds it to the current still album.  Equivalent to the
"Grab Still" button in the Color page.

Returns True if the grab succeeded.
This may require being on the Color page with a valid viewer image.

### `gallery_import_stills`

Import still image files into a Gallery album.

Args:
    file_paths:  List of absolute paths to still image files (e.g.
                 DPX, EXR, TIFF, PNG).
    album_name:  Target album name.  Uses the current album if not
                 specified.

Returns True if the import succeeded.
This method may not be available in all Resolve versions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_paths` | `list[string]` | *required* |  |
| `album_name` | `string` | `None` |  |

### `gallery_set_current_album`

Switch the active still album to the one matching *album_name*.

Args:
    album_name: Exact name of the target still album.

Returns True if the album was switched successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `album_name` | `string` | *required* |  |

### `gallery_set_current_powergrade_album`

Switch the active PowerGrade album to the one matching *album_name*.

Args:
    album_name: Exact name of the target PowerGrade album.

Returns True if the album was switched successfully.
This method may not be available in all Resolve versions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `album_name` | `string` | *required* |  |

## Fairlight

*Audio insertion, presets listing, preset application*

### `fairlight_apply_preset`

Apply a Fairlight audio effect preset to an audio track.

Args:
    preset_name: Exact name of the preset (from fairlight_get_presets).
    track_index: 1-based audio track index to apply the preset to
                 (default 1).  The API may apply the preset globally
                 if per-track targeting is not supported.

Returns True if the preset was applied successfully.
This method may not be available in all Resolve versions.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `preset_name` | `string` | *required* |  |
| `track_index` | `integer` | `1` |  |

### `fairlight_get_presets` `read-only`

List available Fairlight audio effect presets.

Returns preset names as strings.  Returns an empty list if the
Fairlight preset API is not available in this Resolve version.

### `fairlight_insert_audio`

Import an audio file and insert it into the timeline on an audio track.

The file is first imported into the Media Pool, then appended to the
current timeline.  Because the scripting API has limited control over
audio-track targeting, the clip is appended using the standard
AppendToTimeline method.

Args:
    file_path:   Absolute path to the audio file (WAV, MP3, AAC, etc.).
    track_index: 1-based audio track index hint.  The Resolve API may
                 not honour this directly — the clip will be placed on
                 the first available audio track.

Returns True if the audio was inserted successfully.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `string` | *required* |  |
| `track_index` | `integer` | `1` |  |
