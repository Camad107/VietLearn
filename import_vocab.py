"""Import structured Vietnamese vocabulary into VietLearn database."""
from database import get_db, init_db
from datetime import datetime

init_db()

# All vocabulary in order, grouped by category
VOCAB = [
    # === SECTION 1 — MOTS ===

    # Salutations
    ("Xin chào / Chào", "Bonjour / Salut", "Salutations"),
    ("Chào bạn", "Salut (ami)", "Salutations"),
    ("Chào anh", "Bonjour (homme plus âgé)", "Salutations"),
    ("Chào chị", "Bonjour (femme plus âgée)", "Salutations"),
    ("Chào em", "Bonjour (plus jeune)", "Salutations"),
    ("Chào cháu / con", "Bonjour (enfant / neveu)", "Salutations"),
    ("Chào ông", "Bonjour (grand-père / +70 ans)", "Salutations"),
    ("Chào bà", "Bonjour (grand-mère / +70 ans)", "Salutations"),
    ("Chào cô", "Bonjour (femme ~50 ans)", "Salutations"),
    ("Chào chú", "Bonjour (homme ~50 ans)", "Salutations"),
    ("Chào buổi sáng", "Bonjour (matin)", "Salutations"),
    ("Chào buổi chiều", "Bonjour (après-midi)", "Salutations"),
    ("Chào buổi tối", "Bonsoir", "Salutations"),
    ("Chúc ngủ ngon", "Bonne nuit", "Salutations"),

    # Pronoms
    ("Tôi", "Je / Moi (Nord)", "Pronoms"),
    ("Mình", "Je / Moi (Sud)", "Pronoms"),
    ("Bạn", "Tu / Vous (ami)", "Pronoms"),
    ("Anh ấy", "Il (homme plus âgé)", "Pronoms"),
    ("Chị ấy", "Elle (femme plus âgée)", "Pronoms"),
    ("Em ấy", "Il / Elle (plus jeune)", "Pronoms"),
    ("Cô ấy", "Elle (femme ~50 ans)", "Pronoms"),
    ("Bà ấy", "Elle (vieille femme)", "Pronoms"),
    ("Chú ấy", "Il (homme ~50 ans)", "Pronoms"),
    ("Ông ấy", "Il (vieil homme)", "Pronoms"),
    ("Cháu ấy", "Il / Elle (enfant)", "Pronoms"),

    # Verbes
    ("Thích", "Aimer", "Verbes"),
    ("Muốn", "Vouloir", "Verbes"),
    ("Uống", "Boire", "Verbes"),
    ("Ăn", "Manger", "Verbes"),
    ("Có", "Avoir", "Verbes"),
    ("Là", "Être", "Verbes"),
    ("Sống", "Vivre / Habiter", "Verbes"),
    ("Đến", "Venir / Arriver", "Verbes"),
    ("Học", "Apprendre / Étudier", "Verbes"),
    ("Làm việc", "Travailler", "Verbes"),
    ("Xem", "Regarder", "Verbes"),
    ("Ngắm", "Contempler", "Verbes"),
    ("Nói", "Parler", "Verbes"),
    ("Hôn", "Embrasser", "Verbes"),
    ("Kết hôn", "Se marier", "Verbes"),
    ("Ăn chay", "Manger végétarien", "Verbes"),
    ("Ăn trưa", "Déjeuner", "Verbes"),
    ("Có thể", "Pouvoir", "Verbes"),

    # Adjectifs
    ("Ngon", "Délicieux", "Adjectifs"),
    ("Rất", "Très", "Adjectifs"),
    ("Khỏe", "En bonne santé", "Adjectifs"),
    ("Mệt", "Fatigué", "Adjectifs"),
    ("Bình thường", "Normal", "Adjectifs"),
    ("Chay", "Végétarien", "Adjectifs"),

    # Temps
    ("Hôm qua", "Hier", "Temps"),
    ("Hôm nay", "Aujourd'hui", "Temps"),
    ("Ngày mai", "Demain", "Temps"),
    ("Đã", "Passé (marqueur)", "Temps"),
    ("Đang", "Présent (marqueur)", "Temps"),
    ("Sẽ", "Futur (marqueur)", "Temps"),
    ("Buổi sáng", "Matin", "Temps"),
    ("Buổi trưa", "Midi", "Temps"),
    ("Buổi chiều", "Après-midi", "Temps"),
    ("Buổi tối", "Soir", "Temps"),
    ("Bình minh", "Lever du soleil", "Temps"),
    ("Hoàng hôn", "Coucher du soleil", "Temps"),
    ("Chạng vạng", "Crépuscule", "Temps"),
    ("Rồi", "Déjà", "Temps"),
    ("Chưa", "Pas encore", "Temps"),
    ("Nữa", "Plus", "Temps"),
    ("Một lần nữa", "Encore une fois", "Temps"),
    ("Thường", "Souvent", "Temps"),

    # Lieux
    ("Ở", "À / Dans", "Lieux"),
    ("Gần", "Près de", "Lieux"),
    ("Quán", "Café / Restaurant", "Lieux"),
    ("Nhà hàng", "Restaurant", "Lieux"),
    ("Thành phố", "Ville", "Lieux"),
    ("Phường", "Arrondissement", "Lieux"),
    ("Quận", "District", "Lieux"),
    ("Nước / Quốc gia", "Pays", "Lieux"),
    ("Cầu Rồng", "Dragon Bridge", "Lieux"),

    # Identité
    ("Tên", "Nom / Prénom", "Identité"),
    ("Tuổi", "Âge", "Identité"),
    ("Người", "Personne / Nationalité", "Identité"),
    ("Tiếng", "Langue", "Identité"),
    ("Nghề", "Profession", "Identité"),
    ("Giáo viên / Cô giáo", "Professeur (f)", "Identité"),
    ("Thầy giáo", "Professeur (m)", "Identité"),
    ("Bạn gái", "Petite amie", "Identité"),
    ("Bạn trai", "Petit ami", "Identité"),
    ("Người yêu", "Amoureux(se)", "Identité"),

    # Nourriture & Boissons
    ("Cà phê", "Café", "Nourriture & Boissons"),
    ("Cà phê sữa", "Café au lait", "Nourriture & Boissons"),
    ("Cà phê muối", "Café salé", "Nourriture & Boissons"),
    ("Cà phê dừa", "Café coco", "Nourriture & Boissons"),
    ("Cà phê đen", "Café noir", "Nourriture & Boissons"),
    ("Bạc xỉu", "Café très au lait", "Nourriture & Boissons"),
    ("Trà", "Thé", "Nourriture & Boissons"),
    ("Trà đào đá", "Thé pêche glacé", "Nourriture & Boissons"),
    ("Nước ép", "Jus", "Nourriture & Boissons"),
    ("Sinh tố", "Smoothie", "Nourriture & Boissons"),
    ("Sữa", "Lait", "Nourriture & Boissons"),
    ("Sữa dừa", "Lait de coco", "Nourriture & Boissons"),
    ("Sữa đặc", "Lait concentré sucré", "Nourriture & Boissons"),
    ("Sữa chua", "Yaourt", "Nourriture & Boissons"),
    ("Đường", "Sucre", "Nourriture & Boissons"),
    ("Đá", "Glace", "Nourriture & Boissons"),
    ("Bánh mì", "Baguette vietnamienne", "Nourriture & Boissons"),
    ("Cơm chiên", "Riz frit", "Nourriture & Boissons"),
    ("Phở", "Soupe pho", "Nourriture & Boissons"),
    ("Bánh canh cá", "Soupe tapioca poisson", "Nourriture & Boissons"),
    ("Bánh xèo", "Crêpe vietnamienne", "Nourriture & Boissons"),
    ("Bánh cuốn", "Rouleaux de riz", "Nourriture & Boissons"),
    ("Bún riêu", "Soupe vermicelles crabe", "Nourriture & Boissons"),
    ("Bánh hỏi", "Vermicelles fins", "Nourriture & Boissons"),
    ("Mì gói / Mì tôm", "Nouilles instantanées", "Nourriture & Boissons"),
    ("Đậu phụ", "Tofu", "Nourriture & Boissons"),
    ("Trứng", "Œuf", "Nourriture & Boissons"),
    ("Sầu riêng", "Durian", "Nourriture & Boissons"),
    ("Xoài", "Mangue", "Nourriture & Boissons"),
    ("Thơm", "Ananas", "Nourriture & Boissons"),
    ("Táo", "Pomme", "Nourriture & Boissons"),
    ("Tôm", "Crevette", "Nourriture & Boissons"),
    ("Cá", "Poisson", "Nourriture & Boissons"),
    ("Ly", "Verre", "Nourriture & Boissons"),
    ("Tô", "Bol", "Nourriture & Boissons"),
    ("Dĩa / Đĩa", "Assiette", "Nourriture & Boissons"),

    # Nombres
    ("Không", "0", "Nombres"),
    ("Một", "1", "Nombres"),
    ("Hai", "2", "Nombres"),
    ("Ba", "3", "Nombres"),
    ("Bốn / Tư", "4", "Nombres"),
    ("Năm", "5", "Nombres"),
    ("Sáu", "6", "Nombres"),
    ("Bảy", "7", "Nombres"),
    ("Tám", "8", "Nombres"),
    ("Chín", "9", "Nombres"),
    ("Mười", "10", "Nombres"),
    ("Mươi", "Dizaines", "Nombres"),
    ("Trăm", "Cent", "Nombres"),
    ("Nghìn / Ngàn", "Mille", "Nombres"),
    ("Triệu", "Million", "Nombres"),
    ("Tỷ", "Milliard", "Nombres"),
    ("Bao nhiêu", "Combien", "Nombres"),
    ("Bao lâu", "Depuis combien de temps", "Nombres"),

    # Connecteurs
    ("Và", "Et", "Connecteurs"),
    ("Với", "Avec", "Connecteurs"),
    ("Nhưng", "Mais", "Connecteurs"),
    ("Hay / Hoặc", "Ou", "Connecteurs"),
    ("Thích ... hơn", "Préférer", "Connecteurs"),
    ("Cả hai", "Les deux", "Connecteurs"),
    ("Không", "Non / Ne pas", "Connecteurs"),
    ("Cũng", "Aussi", "Connecteurs"),
    ("Cũng vậy", "Pareil", "Connecteurs"),
    ("Một chút", "Un peu", "Connecteurs"),
    ("Còn ... ?", "Et ... ?", "Connecteurs"),
    ("Gì", "Quoi", "Connecteurs"),
    ("Ở đâu", "Où", "Connecteurs"),
    ("Nào", "Lequel", "Connecteurs"),
    ("Cho", "Donner / Commander", "Connecteurs"),
    ("Nha", "S'il te plaît", "Connecteurs"),
    ("Ơi", "Hé / Excuse-moi", "Connecteurs"),
    ("Phải không", "C'est ça ?", "Connecteurs"),
    ("Đúng không", "N'est-ce pas", "Connecteurs"),
    ("Phải rồi / Đúng rồi", "Exact", "Connecteurs"),
    ("Không phải", "Ce n'est pas ça", "Connecteurs"),
    ("Giờ", "Heure", "Connecteurs"),
    ("Tháng", "Mois", "Connecteurs"),

    # Expressions utiles
    ("Cảm ơn", "Merci", "Expressions utiles"),
    ("Không có gì", "De rien", "Expressions utiles"),
    ("Không sao", "Pas de problème", "Expressions utiles"),
    ("Rất vui được gặp bạn", "Ravi de te rencontrer", "Expressions utiles"),
    ("Cố lên", "Courage", "Expressions utiles"),
    ("Chúc mừng năm mới", "Bonne année", "Expressions utiles"),
    ("Tết", "Nouvel an lunaire", "Expressions utiles"),
    ("Lì xì", "Argent porte-bonheur", "Expressions utiles"),

    # === SECTION 2 — PHRASES ===

    # Leçon 1
    ("Mình thích cà phê", "J'aime le café", "Leçon 1"),
    ("Mình thích ăn bún riêu", "J'aime manger bún riêu", "Leçon 1"),
    ("Mình có một con chó", "J'ai un chien", "Leçon 1"),
    ("Anh ấy thích uống cà phê muối", "Il aime boire café salé", "Leçon 1"),
    ("Em ấy thích ăn bánh mì", "Elle aime manger bánh mì", "Leçon 1"),
    ("Mình thích ăn bún riêu với đậu phụ", "J'aime bún riêu avec tofu", "Leçon 1"),
    ("Em không muốn uống nữa", "Je ne veux plus boire", "Leçon 1"),
    ("Em thích uống cà phê sữa hay cà phê muối ?", "Tu préfères café au lait ou café salé ?", "Leçon 1"),

    # Leçon 2
    ("Em tên là Elia", "Je m'appelle Elia", "Leçon 2"),
    ("Em 25 tuổi", "J'ai 25 ans", "Leçon 2"),
    ("Em đến từ Pháp", "Je viens de France", "Leçon 2"),
    ("Em là người Pháp", "Je suis français", "Leçon 2"),
    ("Em sống ở thành phố Đà Nẵng", "J'habite à Da Nang", "Leçon 2"),
    ("Em đến Việt Nam một tháng rồi", "Je suis au Vietnam depuis un mois", "Leçon 2"),
    ("Em là giáo viên tiếng Anh", "Je suis professeur d'anglais", "Leçon 2"),
    ("Rất vui được gặp chị", "Ravi de te rencontrer", "Leçon 2"),
    ("Chị ơi cho em một tô bánh canh cá lóc", "Un bol de soupe s'il vous plaît", "Leçon 2"),
    ("Chị ơi cho em một ly trà", "Un verre de thé s'il vous plaît", "Leçon 2"),

    # Leçon 3
    ("Mình ăn chay và thích ăn cơm chiên chay", "Je suis végétarien et j'aime le riz frit végé", "Leçon 3"),
    ("Bạn thích cơm chiên không ?", "Tu aimes le riz frit ?", "Leçon 3"),
    ("Mình thích uống cà phê dừa", "J'aime boire café coco", "Leçon 3"),
    ("Mình thích ăn bánh mì vào buổi sáng", "J'aime manger bánh mì le matin", "Leçon 3"),
    ("Mình thích uống nước ép vào buổi sáng", "J'aime boire jus le matin", "Leçon 3"),

    # Leçon 4
    ("Mình tên là Adrien và 32 tuổi", "Je m'appelle Adrien et j'ai 32 ans", "Leçon 4"),
    ("Mình là người Pháp nhưng sống ở Đà Nẵng", "Je suis français mais j'habite à Da Nang", "Leçon 4"),
    ("Mình làm việc online", "Je travaille en ligne", "Leçon 4"),
    ("Bánh mì rất ngon", "Le bánh mì est délicieux", "Leçon 4"),

    # Leçon 5
    ("Hôm qua con đã ăn cơm chiên với trứng", "Hier j'ai mangé riz frit avec œuf", "Leçon 5"),
    ("Hôm nay con đang học tiếng Việt", "Aujourd'hui j'apprends le vietnamien", "Leçon 5"),
    ("Ngày mai con sẽ xem phim", "Demain je regarderai un film", "Leçon 5"),
    ("Con khỏe không ?", "Comment ça va ?", "Leçon 5"),
    ("Con khỏe", "Ça va", "Leçon 5"),
    ("Con tên là gì ?", "Comment tu t'appelles ?", "Leçon 5"),
    ("Con thích ăn gì ?", "Tu veux manger quoi ?", "Leçon 5"),
    ("Con đến từ đâu ?", "Tu viens d'où ?", "Leçon 5"),

    # Leçon 6
    ("Bạn bao nhiêu tuổi ?", "Quel âge as-tu ?", "Leçon 6"),
    ("Bạn đến Việt Nam bao lâu rồi ?", "Depuis combien de temps es-tu au Vietnam ?", "Leçon 6"),
    ("Bạn sống ở đâu ?", "Où habites-tu ?", "Leçon 6"),
    ("Bạn làm nghề gì ?", "Quel est ton métier ?", "Leçon 6"),
    ("Bạn kết hôn chưa ?", "Es-tu marié ?", "Leçon 6"),
    ("Bạn có bạn gái chưa ?", "As-tu une petite amie ?", "Leçon 6"),

    # Leçon 7
    ("Bạn ăn trưa chưa ?", "As-tu déjeuné ?", "Leçon 7"),
    ("Mình chưa ăn", "Pas encore mangé", "Leçon 7"),
    ("Mình ăn rồi", "Déjà mangé", "Leçon 7"),
    ("Bạn uống cà phê chưa ?", "As-tu bu ton café ?", "Leçon 7"),
    ("Cho mình một ly cà phê sữa nha", "Un café au lait s'il te plaît", "Leçon 7"),

    # Leçon 8
    ("Mình có thể nói tiếng Anh, tiếng Pháp và một chút tiếng Việt", "Je peux parler anglais, français et un peu vietnamien", "Leçon 8"),
    ("Mình ăn được sầu riêng", "Je peux manger du durian", "Leçon 8"),
    ("Mình không ăn được sầu riêng", "Je ne peux pas manger du durian", "Leçon 8"),
    ("Mình thường uống cà phê sữa vào buổi sáng", "Je bois souvent café au lait le matin", "Leçon 8"),
]

# Category display order
CATEGORY_ORDER = [
    "Salutations", "Pronoms", "Verbes", "Adjectifs", "Temps", "Lieux",
    "Identité", "Nourriture & Boissons", "Nombres", "Connecteurs",
    "Expressions utiles",
    "Leçon 1", "Leçon 2", "Leçon 3", "Leçon 4",
    "Leçon 5", "Leçon 6", "Leçon 7", "Leçon 8",
]

db = get_db()
now = datetime.now().isoformat()
count = 0

for viet, french, category in VOCAB:
    cur = db.execute(
        "INSERT INTO vocabulary (vietnamese, french, category, created_at) VALUES (?, ?, ?, ?)",
        (viet, french, category, now)
    )
    db.execute(
        "INSERT INTO review_stats (vocab_id, next_review) VALUES (?, ?)",
        (cur.lastrowid, now)
    )
    count += 1

db.commit()
db.close()
print(f"Imported {count} entries")
