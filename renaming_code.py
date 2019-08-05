
#add prefix to images from drone
cd /D R:\MarineUAS\Projects\Client Projects\LTER\LTER 2019\Palmer 2019 UAS whale data\Filed by convention\190305_L\Flight_04\Sony
for %a in (DSC*) do ren "%a" "190305_L_F4_%a"

#add prefix to GOPRO videos
cd /D R:\MarineUAS\Projects\Client Projects\LTER\LTER 2018\LTER2018 - updated format\180125_A\Flight_01\GoPro
for %a in (G*) do ren "%a" "180125_A_F1_%a"

#add prefix to images in indiviudal folder
cd /D R:\MarineUAS\Projects\Client Projects\LTER\LTER 2017\LTER2017-updated_useforPhotogram\Individuals\Mn170106_A_F1_01
for %a in (DSC*) do ren "%a" "170106_A_F1_%a"

#remove old prefix and add new prefix
# 1 / per character you want to remove
cd /D R:\MarineUAS\Projects\Client Projects\LTER\LTER 2017\Alta_UpdateFileStructure_ForPhotogram\170202_A\Flight_02\Sony
for %a in (2*) do ren "%a" "///////////*"
for %a in (DSC*) do ren "%a" "170202_A_F2_%a"


cd /D R:\MarineUAS\Projects\Client Projects\UK Dolphing Photogrammetry\170801_L\Flight_02\Sony
for %a in (1*) do ren "%a" "///////*"
for %a in (DSC*) do ren "%a" "170801_L_F2_%a"

cd /D R:\MarineUAS\Projects\Client Projects\LTER\LTER 2017\LTER2017-updated_useforPhotogram\Individuals\Mn170202_A_F2_07
for %a in (2*) do ren "%a" "///////////*"
for %a in (DSC*) do ren "%a" "170202_A_F2_%a"

for %a in (F3*) do ren "%a" "170108_A_%a"

cd /D R:\MarineUAS\Projects\Student Projects\KCBierlich\Data\ErrorExperiment\190626_A\Flight_02\Images
for %a in (*) do ren "%a" "190626_A_F2_%a"

for %a in (D*) do ren "%a" "////*"
