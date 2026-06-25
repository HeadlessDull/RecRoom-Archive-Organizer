# RecRoom-Archive-Organizer
Simple program used internally to orginize images

## What it does

Drop in PNG images, pick the asset type and category, give it a name and it
automatically builds the correct folder structure inside the local GitHub clone

### Folder logic

| Type           | Destination                                        |
|----------------|----------------------------------------------------|
| Clothing Item  | `RecRoom-Avatar-Archive/Items/<Category>/<Name>/`  |
| Prop           | `RecRoom-Avatar-Archive/Props/<Category>/<Name>/`  |
| Map            | `RecRoom-World-Archive/Maps/<Name>/`               |
| NPC            | `RecRoom-World-Archive/NPCs/<Name>/`               |

**Single image:** copied directly into the item folder (no subfolders).  
**Multiple images:** each image gets its own subfolder named after the PNG file,
plus one randomly chosen image is placed in the parent folder as the cover/preview.


## How to use

1. Run `RR Archive Organizer.exe`.
2. Set your **GitHub folder** the parent directory that contains your repo folders  
   e.g. `C:\Users\You\Documents\GitHub`
3. Choose the **Asset type** (Clothing Item / Prop / Map / NPC).
4. Pick the **Category** (shown for Clothing and Props).
5. Enter the **item name** (this becomes the new folder).
6. Click **+ Add images** and select your PNGs.
7. Click:  Organise Files**.
