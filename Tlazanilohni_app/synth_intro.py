"""Synthesize the Tlapannextiliztli intro in all 3 voice variants and save to VoiceComparison/."""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from main import synthesize, post_tts, concat_wavs

TEXT = (
    "Hueliz tiquixmatiya Crispin Martinez Rosas. "
    "Yehyectzin quen huica, yeyectizin quen tlatzotzona, yehyectzin huicaliztli tlen quiihcuilohtoc: "
    '"Nimitzillamiqui", "Canin tinemi", "Xinolah", "Tateh Juan". '
    "Huan naman quipannextia achtoui in amox, Tlallamiquiliztli inelhuayo. "
    "Nelpatiyoh ni xochitlapohualiztli. "
    "Quemman pehuaz ticpohuaz, axcanah hueliz ticcahuaz pampa amoxtli mitztilanaz huan mitztcalaquiz "
    "pan pilaltepetzin campa nemih miac macehualmeh tlen tiquinixmatihya: macehualmeh tlen tlatlepanittah "
    "huan cequinoqueh tlen tepazhuiah; tlalichtequinin tlen quintotocah macehualmeh huan quitlatiah "
    "ininchan huan ininmillah; telpocatl tlen quiichtequi ichpocatl huan iuhquinhon mocihuatia pampa "
    "prohueh huan axcanah quiceliah ichpocatl itatahuan; cihuameh tlen mochicahuiliah huan momanahuiah "
    "quemman pano tlamantli tlen axcualli; telpocatl tlen yohui Mexco huan axcanah quiihyohuia nemiliztli "
    "tlen huei altepetl; macehualmeh tlen cualli quimatih quixolehuazceh nochi tlamantli cualantli pan "
    "pilatepetzin; macehualmeh tlen mohmoztla tequitih huan mopalehuiah. "
    "Nouhquiya tiquiittaz rohuenteh tlen quinhuilana macehualmeh cuatitlan; axcanelimeh tlen anotzah; "
    "papameh tlen quinmanextiah macehualmeh canin yohuih; cuatitlan iteucco tlen quinmanahuia tecuanimeh; "
    "tonatiuh tlen moixchichilohtoc pampa quitta nochi tlen pano huan pinahua. "
    "Tiquillamiquiz yoltoc nochi tlen oncah tlaticpac huan ilhuicac. "
    "Huan timotlahtlaniz tlan tlamantli tlen mictoc nocca hueli chamaniz. "
    "Tlahcuilohtquetl techhuica canin nemiyayah itotatahhuan, itatahhuan huan iteixmatcahuan, "
    "pan ni canahya tlen zanzampa tecyolpactia huan techcuezoa, pan ni macehualtlaltepactli tlen ya "
    "quichihchihua, quinextia, quiyoltilia huan quichamanaltia ica itlahcuiloliz. "
    "Itlahtol calaquiz huan mocauhtihcaz pan tonehnehuiliz huan totlailnamiquiliz. "
    "Ica iamox, tocompah Crispin quitlapoa iyollo quence tezcatl, huan yeca tlahuel tictlazcamatiliah."
)

OUT_DIR = "/storage/emulated/0/Music/Tlazanilohni/VoiceComparison"
os.makedirs(OUT_DIR, exist_ok=True)

VARIANTS = [
    ("voice3",         "intro_3_voice3.wav"),
    ("default,voice3", "intro_5_blend_v1v3.wav"),
]

for voice_str, filename in VARIANTS:
    voices = [v.strip() for v in voice_str.split(",")]
    print(f"\n=== {filename} (voices: {voices}) ===")
    audio = synthesize(TEXT, voices)
    path = os.path.join(OUT_DIR, filename)
    with open(path, "wb") as f:
        f.write(audio)
    print(f"Saved: {path}")

print("\nAll 3 versions saved to Music/Tlazanilohni/VoiceComparison/")
