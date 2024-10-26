	.assume adl=1   
    .org 0x040000    

    jp start       

    .align 64      
    .db "MOS"       
    .db 00h         
    .db 01h       

start:              
    push af
    push bc
    push de
    push ix
    push iy

	call main

exit:
    pop iy
    pop ix
    pop de
    pop bc
    pop af
    ld hl,0
    ret

; API includes
    include "mos_api.inc"
    include "functions.inc"
    include "files.inc"
    include "timer.inc"
    include "vdu.inc"
    include "vdu_fonts.inc"

; Application includes
    include "fonts_list.inc"
    include "cfg.inc"

main:
    ld a,screen_mode
    call vdu_set_screen_mode

; ; print test string
;     call printNewLine
;     ld hl,uxor_balnea
;     call printString
;     call printNewLine

; inputs: hl = bufferId; iy = pointer to filename
    ld e,font_name
    ld d,12 ; bytes per font list record
    mlt de
    ld iy,font_list
    add iy,de
    push iy

    ld iy,(iy+9)

; debug print filename at iy
    call printNewLine
    push iy
    pop hl
    call printString
    call printNewLine

    ld hl,0x4000 ; bufferId
    push hl
    call vdu_load_buffer_from_file

; create font from buffer
; inputs: hl = bufferId, e = width, d = height, d = ascent, a = flags
; VDU 23, 0, &95, 1, bufferId; width, height, ascent, flags: Create font from buffer
    pop hl ; bufferId
    pop iy ; pointer to font list record
    push hl
    ld a,(iy+0)
    ld e,a  ; width
    ld a,(iy+3)
    ld d,a  ; height / ascent
    ld a,0 ; flags
    call vdu_font_create

; select font
; inputs: hl = bufferId, a = font flags
; Flags:
; Bit	Description
; 0	Adjust cursor position to ensure text baseline is aligned
;   0: Do not adjust cursor position (best for changing font on a new line)
;   1: Adjust cursor position (best for changing font in the middle of a line)
; 1-7	Reserved for future use
; VDU 23, 0, &95, 0, bufferId; flags: Select font
    pop hl
    ld a,0
    call vdu_font_select

; print test string
    call printNewLine
    ld hl,lorem_ipsum
    call printString
    call printNewLine

; print test string
    ld hl,test_string
    call printString
    call printNewLine

; all done
    ret

test_string:
    db 0x20,0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29,0x2A,0x2B,0x2C,0x2D,0x2E,0x2F
    db 0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3A,0x3B,0x3C,0x3D,0x3E,0x3F
    db 0x40,0x41,0x42,0x43,0x44,0x45,0x46,0x47,0x48,0x49,0x4A,0x4B,0x4C,0x4D,0x4E,0x4F
    db 0x50,0x51,0x52,0x53,0x54,0x55,0x56,0x57,0x58,0x59,0x5A,0x5B,0x5C,0x5D,0x5E,0x5F
    db 0x60,0x61,0x62,0x63,0x64,0x65,0x66,0x67,0x68,0x69,0x6A,0x6B,0x6C,0x6D,0x6E,0x6F
    db 0x70,0x71,0x72,0x73,0x74,0x75,0x76,0x77,0x78,0x79,0x7A,0x7B,0x7C,0x7D,0x7E,0x7F
    db 0x80,0x81,0x82,0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x8A,0x8B,0x8C,0x8D,0x8E,0x8F
    db 0x90,0x91,0x92,0x93,0x94,0x95,0x96,0x97,0x98,0x99,0x9A,0x9B,0x9C,0x9D,0x9E,0x9F
    db 0xA0,0xA1,0xA2,0xA3,0xA4,0xA5,0xA6,0xA7,0xA8,0xA9,0xAA,0xAB,0xAC,0xAD,0xAE,0xAF
    db 0xB0,0xB1,0xB2,0xB3,0xB4,0xB5,0xB6,0xB7,0xB8,0xB9,0xBA,0xBB,0xBC,0xBD,0xBE,0xBF
    db 0xC0,0xC1,0xC2,0xC3,0xC4,0xC5,0xC6,0xC7,0xC8,0xC9,0xCA,0xCB,0xCC,0xCD,0xCE,0xCF
    db 0xD0,0xD1,0xD2,0xD3,0xD4,0xD5,0xD6,0xD7,0xD8,0xD9,0xDA,0xDB,0xDC,0xDD,0xDE,0xDF
    db 0xE0,0xE1,0xE2,0xE3,0xE4,0xE5,0xE6,0xE7,0xE8,0xE9,0xEA,0xEB,0xEC,0xED,0xEE,0xEF
    db 0xF0,0xF1,0xF2,0xF3,0xF4,0xF5,0xF6,0xF7,0xF8,0xF9,0xFA,0xFB,0xFC,0xFD,0xFE,0xFF,13,10
    db 0x00

lorem_ipsum:
    db "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    db "Nulla autem virtuosa tristitia, sed gloria virtutis in ipso est. "
    db "Nam sapientis animum fluctibus movet; in vita, res novae, "
    db "novas tempestates ferunt. Fortis enim est, qui dolorem, cum "
    db "potest, arcet. Nemo tam divitiis abundat, qui, si desit libertas, "
    db "beatus. Hic igitur ratio victum etiam sine voluptas quaerit. "
    db "Nam in medio stat virtus: tam paupertas quam divitiae vitandae. "
    db "Mens sibi conscia recti, semper aditum ad libertatem invocat. "
    db "Quid est enim aliud esse versutum? Quod si ita se habeat, "
    db "non possit beatam praestare vitam sapientia. Quamquam tu hanc "
    db "cognitionem, Quirine, si tibi probatur, repudiandam non esse "
    db "dices. Quae cum dixisset paulumque institisset, Quid est?"
    db "\r\n\r\n"

pullo_vorenus:
    db "Erant in ea legione fortissimi viri, centuriones, qui primis "
    db "ordinibus appropinquarent, Titus Pullo et Lucius Vorenus. "
    db "Hi perpetuas inter se controversias habebant, quinam "
    db "anteferretur, omnibusque annis de locis summis "
    db "simultatibus contendebant."
    db "\r\n\r\n"
    db "Cum acerrime ad munitiones pugnaretur, Pullo exclamat: "
    db "'Quid dubitas, Vorene? Aut quem locum tuae virtutis "
    db "exspectas?' Statim extra munitiones procedit, et ubi "
    db "hostes confertissimi sunt, irrumpit. Vorenus, "
    db "existimationem veritus, eum sequitur et tela conicit."
    db "\r\n\r\n"
    db "Pullo gladio impeditus circumvenitur; Vorenus auxilium "
    db "fert et hostes propellit. Ambo, compluribus interfectis, "
    db "cum summa laude intra munitiones redeunt. Sic fortuna "
    db "in contentione utrumque versavit, ut uter utri auxilio "
    db "fuerit nec diiudicari posset, uter virtute anteferendus "
    db "videretur."
    db "\r\n\r\n", 0

uxor_balnea:
    db "Erat mulier, uxor Balnea, quae quinque viros tenuit sub vinculo "
    db "matrimonii, una post alterum, et omnis vitam per amorem egit. "
    db "Nulla mors amoris ipsam superavit. Cui rogatus est, vir novus, "
    db "de matrimonio. At narravit fabulam miram, magna et risum."
    db "\r\n\r\n"
    db "Adeo fabula incepit: Vir nobilis, eques, in diebus Arthuri, errans "
    db "per silvas obscuras, invenit puellam pulcherrimam. Sed, ah, homo "
    db "luxuriae succubuit; deliquit eam contra voluntatem. Rex dedit "
    db "eum damnum multum, et iussit mortem. Regina tamen eius vitam "
    db "servavit, sed tantum si responsum verum ad quaestionem sciret: "
    db "'Quid volunt mulieres vere?'. Ita iter periculosum cepit."
    db "\r\n\r\n"
    db 0
    db "Eques per terras erravit, quaerens responsum ab omnibus: damas "
    db "divas, ancillas, et vetulas. Quis rogavit, varia respondit; nescivit "
    db "vere, quid volunt mulieres, donec foemina vetus decrepita, sed "
    db "sapientia abundans, obtulit ei responsum rectum. Pretium erat "
    db "parvulum, vel, sic putavit ille. Nam vetula rogavit quod ipse "
    db "eam uxoraret. Illum hoc taeduit, sed voto facto, promissum tenuit."
    db "\r\n\r\n"
    db "In nuptiali die, vetula dixit: 'Mulieres volunt dominari in vita; "
    db "velint regnum suum tenere, dominam esse in domo et anima "
    db "sua libere vivere.' Hoc scivit verum esse, et licentiam in vitam "
    db "ipsam dedit ut ipsa dominaretur. Tunc mutatio mirabilis facta!"
    db "\r\n\r\n"
    db "Vetula ipsa repente pulcherrima facta est, iuvenis mulier dulcis "
    db "atque praeclara. Et eques tandem laetus fuit; ex illo die beatus, "
    db "quod sibi consortem novam benigneque passus est dominam. "
    db "Amorem suum vera vidit: non tantum pulchritudinem quaesivit "
    db "sed libertatem suam ac respectum quae amica vere debet."
    db "\r\n\r\n"
    db "Sic uxor Balnea, fabulam finiens, risit amice, exemplo vitae suae. "
    db "Ipsa, quinque viris domitam, vel audaciam habuit de vita docere. "
    db "Licet risum multum ferre, fabula ipsa veritatem sapientem tenet: "
    db "ipsa vita est dulcis, et in amore pari dominatio verum gaudium."
    db "\r\n\r\n"
    db 0

wife_of_bath:
    db "She was a woman, wife of Bath, who held five husbands in her "
    db "matrimonial chains, one after another, and lived all through love. "
    db "No fear of loss could conquer her. When a new man asked her "
    db "for marriage, she told him a marvelous tale, great and merry."
    db "\r\n\r\n"
    db "So the tale begins: A noble knight, in Arthur's days, wandered "
    db "through shadowed woods and found a lovely young maiden. Alas, "
    db "the man fell to his lust and wronged her against her will. The king "
    db "sentenced him to death, but the queen spared his life, if only he "
    db "could answer one true question: 'What do women truly want?' So, "
    db "he began a perilous quest."
    db "\r\n\r\n"
    db "The knight roamed far, seeking answers from all: fine ladies, "
    db "maids, even old women. Each gave him something different; he "
    db "had no true answer, until a shriveled crone, wise in knowledge, "
    db "offered him the right response. But her price was small, or so he "
    db "thought--for the old woman demanded he wed her. Loath, but "
    db "bound by his vow, he kept his word."
    db "\r\n\r\n"
    db "On their wedding day, the crone said: 'Women wish for mastery, "
    db "to hold their realm, to be the lady at home and in heart, and "
    db "to live free in spirit.' He knew this to be true, so he gave her "
    db "freedom in their life together. Then, a wondrous change took place!"
    db "\r\n\r\n"
    db "The old crone transformed, becoming young, sweet, and fair. "
    db "The knight was overjoyed; from that day forth he was blessed, "
    db "for his new bride was both noble and gentle. In her, he saw real "
    db "love: not just beauty, but the freedom and respect a true partner "
    db "deserves."
    db "\r\n\r\n"
    db "Thus, the wife of Bath, ending her tale, laughed fondly, with "
    db "a lesson from her own life. With five husbands tamed, she had "
    db "dared to teach on life and love. Though jesting, her tale held "
    db "wisdom: life is sweet, and in equal love, true joy is shared."
    db "\r\n\r\n"
    db 0