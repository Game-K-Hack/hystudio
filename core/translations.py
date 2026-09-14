"""Table des traductions : cle = texte francais du code.

Ordre des colonnes de L() : en, es, de, it, ru, zh, ja, ko. fr= corrige
l'affichage francais quand la cle n'est pas le texte final.
"""


def L(en, es, de, it, ru, zh, ja, ko, fr=None):
    d = dict(en=en, es=es, de=de, it=it, ru=ru, zh=zh, ja=ja, ko=ko)
    if fr is not None:
        d["fr"] = fr
    return d


TABLE = {
    # ------------------------------------------------------------ menus
    "&Fichier": L("&File", "&Archivo", "&Datei", "&File", "&Файл", "文件(&F)", "ファイル(&F)", "파일(&F)"),
    "&Édition": L("&Edit", "&Edición", "&Bearbeiten", "&Modifica", "&Правка", "编辑(&E)", "編集(&E)", "편집(&E)"),
    "&Langue": L("&Language", "&Idioma", "&Sprache", "&Lingua", "&Язык", "语言(&L)", "言語(&L)", "언어(&L)"),
    "Automatique (langue du système)": L(
        "Automatic (system language)", "Automático (idioma del sistema)", "Automatisch (Systemsprache)",
        "Automatica (lingua di sistema)", "Автоматически (язык системы)", "自动（系统语言）",
        "自動（システムの言語）", "자동 (시스템 언어)"),
    "Nouveau projet depuis un modèle 3D…": L(
        "New project from a 3D model…", "Nuevo proyecto a partir de un modelo 3D…", "Neues Projekt aus 3D-Modell…",
        "Nuovo progetto da un modello 3D…", "Новый проект из 3D-модели…", "从 3D 模型新建项目…",
        "3D モデルから新規プロジェクト…", "3D 모델로 새 프로젝트…"),
    "Ouvrir un projet…": L("Open project…", "Abrir proyecto…", "Projekt öffnen…", "Apri progetto…",
                           "Открыть проект…", "打开项目…", "プロジェクトを開く…", "프로젝트 열기…"),
    "Enregistrer": L("Save", "Guardar", "Speichern", "Salva", "Сохранить", "保存", "保存", "저장"),
    "Enregistrer sous…": L("Save as…", "Guardar como…", "Speichern unter…", "Salva con nome…",
                           "Сохранить как…", "另存为…", "名前を付けて保存…", "다른 이름으로 저장…"),
    "Recharger le profil Hyundai i20 validé": L(
        "Reload the validated Hyundai i20 profile", "Recargar el perfil validado del Hyundai i20",
        "Validiertes Hyundai-i20-Profil neu laden", "Ricarica il profilo Hyundai i20 validato",
        "Загрузить проверенный профиль Hyundai i20", "重新加载已验证的 Hyundai i20 配置",
        "検証済みの Hyundai i20 プロファイルを再読み込み", "검증된 Hyundai i20 프로필 다시 불러오기"),
    "Quitter": L("Quit", "Salir", "Beenden", "Esci", "Выход", "退出", "終了", "끝내기"),
    "Annuler": L("Undo", "Deshacer", "Rückgängig", "Annulla", "Отменить", "撤销", "元に戻す", "실행 취소"),
    "Rétablir": L("Redo", "Rehacer", "Wiederherstellen", "Ripeti", "Повторить", "重做", "やり直し", "다시 실행"),
    "Rien à annuler.": L("Nothing to undo.", "Nada que deshacer.", "Nichts rückgängig zu machen.",
                         "Niente da annullare.", "Нечего отменять.", "没有可撤销的操作。", "元に戻す操作はありません。",
                         "실행 취소할 작업이 없습니다."),
    "Rien à rétablir.": L("Nothing to redo.", "Nada que rehacer.", "Nichts wiederherzustellen.",
                          "Niente da ripetere.", "Нечего повторять.", "没有可重做的操作。", "やり直す操作はありません。",
                          "다시 실행할 작업이 없습니다."),
    "Annulé.": L("Undone.", "Deshecho.", "Rückgängig gemacht.", "Annullato.", "Отменено.", "已撤销。",
                 "元に戻しました。", "실행 취소했습니다."),
    "Rétabli.": L("Redone.", "Rehecho.", "Wiederhergestellt.", "Ripetuto.", "Повторено.", "已重做。",
                  "やり直しました。", "다시 실행했습니다."),
    "Interrompu.": L("Cancelled.", "Interrumpido.", "Abgebrochen.", "Interrotto.", "Прервано.", "已中止。",
                     "中止しました。", "중단했습니다.", fr="Annulé."),
    "Changement de langue": L("Language change", "Cambio de idioma", "Sprachwechsel", "Cambio di lingua",
                              "Смена языка", "切换语言", "言語の切り替え", "언어 변경"),
    "Un calcul ou une copie est en cours : la langue choisie s'appliquera au prochain démarrage.": L(
        "A render or copy is in progress: the chosen language will apply at the next start.",
        "Hay un cálculo o una copia en curso: el idioma elegido se aplicará en el próximo inicio.",
        "Eine Berechnung oder Kopie läuft: Die gewählte Sprache gilt ab dem nächsten Start.",
        "È in corso un calcolo o una copia: la lingua scelta verrà applicata al prossimo avvio.",
        "Идёт расчёт или копирование: выбранный язык будет применён при следующем запуске.",
        "正在计算或复制：所选语言将在下次启动时生效。",
        "計算またはコピーの実行中です。選択した言語は次回の起動時に適用されます。",
        "계산 또는 복사가 진행 중입니다. 선택한 언어는 다음 시작 시 적용됩니다."),

    "À propos de HyStudio": L("About HyStudio", "Acerca de HyStudio", "Über HyStudio", "Informazioni su HyStudio",
                               "О программе HyStudio", "关于 HyStudio", "HyStudio について", "HyStudio 정보"),
    "Personnalisez un modèle 3D de voiture et produisez sa rotation 360° pour l'autoradio.": L(
        "Customize a 3D car model and produce its 360° rotation for the head unit.",
        "Personalice un modelo 3D de coche y genere su rotación de 360° para la radio.",
        "Passen Sie ein 3D-Automodell an und erzeugen Sie seine 360°-Drehung für das Autoradio.",
        "Personalizza un modello 3D di auto e produci la sua rotazione a 360° per l'autoradio.",
        "Настройте 3D-модель автомобиля и создайте её 360° вращение для магнитолы.",
        "自定义 3D 汽车模型，并为车机生成 360° 旋转动画。",
        "車の 3D モデルをカスタマイズし、カーナビ用の 360° 回転を作成します。",
        "자동차 3D 모델을 꾸미고 카오디오용 360° 회전을 만듭니다."),

    "Rechercher des mises à jour…": L(
        "Check for updates…", "Buscar actualizaciones…", "Nach Updates suchen…", "Cerca aggiornamenti…",
        "Проверить обновления…", "检查更新…", "更新を確認…", "업데이트 확인…"),
    "Mises à jour": L("Updates", "Actualizaciones", "Updates", "Aggiornamenti", "Обновления", "更新", "更新", "업데이트"),
    "Mise à jour disponible": L(
        "Update available", "Actualización disponible", "Update verfügbar", "Aggiornamento disponibile",
        "Доступно обновление", "有可用更新", "更新があります", "업데이트 가능"),
    "MAJ_DISPO": L(
        "A new version of HyStudio is available (you are using {cur}): version {new}.\n\n"
        "Your projects and models are kept: only the software is replaced. HyStudio will restart once installed.",
        "Hay una nueva versión de HyStudio disponible (usa la {cur}): versión {new}.\n\n"
        "Sus proyectos y modelos se conservan: solo se sustituye el programa. HyStudio se reiniciará al terminar.",
        "Eine neue HyStudio-Version ist verfügbar (Sie nutzen {cur}): Version {new}.\n\n"
        "Ihre Projekte und Modelle bleiben erhalten: Nur die Software wird ersetzt. HyStudio startet danach neu.",
        "È disponibile una nuova versione di HyStudio (in uso: {cur}): versione {new}.\n\n"
        "Progetti e modelli vengono conservati: viene sostituito solo il programma. HyStudio si riavvierà al termine.",
        "Доступна новая версия HyStudio (у вас {cur}): версия {new}.\n\n"
        "Ваши проекты и модели сохранятся: заменяется только программа. После установки HyStudio перезапустится.",
        "HyStudio 有新版本可用（当前 {cur}）：{new} 版。\n\n您的项目和模型会保留，只替换软件本身。安装完成后 HyStudio 将重新启动。",
        "HyStudio の新しいバージョンがあります（現在 {cur}）：バージョン {new}。\n\n"
        "プロジェクトとモデルはそのまま残り、ソフトウェアだけが置き換えられます。インストール後に HyStudio が再起動します。",
        "새 HyStudio 버전을 사용할 수 있습니다 (현재 {cur}): 버전 {new}.\n\n"
        "프로젝트와 모델은 그대로 유지되며 프로그램만 교체됩니다. 설치 후 HyStudio가 다시 시작됩니다.",
        fr="Une nouvelle version de HyStudio est disponible (vous utilisez la {cur}) : version {new}.\n\n"
           "Vos projets et vos modèles sont conservés : seul le logiciel est remplacé. "
           "HyStudio redémarrera une fois installé."),
    "Mettre à jour": L("Update", "Actualizar", "Aktualisieren", "Aggiorna", "Обновить", "更新", "更新する", "업데이트"),
    "Plus tard": L("Later", "Más tarde", "Später", "Più tardi", "Позже", "稍后", "後で", "나중에"),
    "Ignorer cette version": L(
        "Skip this version", "Omitir esta versión", "Diese Version überspringen", "Ignora questa versione",
        "Пропустить эту версию", "跳过此版本", "このバージョンをスキップ", "이 버전 건너뛰기"),
    "Ouvrir la page de téléchargement": L(
        "Open the download page", "Abrir la página de descarga", "Download-Seite öffnen", "Apri la pagina di download",
        "Открыть страницу загрузки", "打开下载页面", "ダウンロードページを開く", "다운로드 페이지 열기"),
    "Téléchargement de la mise à jour…": L(
        "Downloading the update…", "Descargando la actualización…", "Update wird heruntergeladen…",
        "Download dell'aggiornamento…", "Загрузка обновления…", "正在下载更新…", "更新をダウンロード中…",
        "업데이트 다운로드 중…"),
    "HyStudio est à jour (version {v}).": L(
        "HyStudio is up to date (version {v}).", "HyStudio está actualizado (versión {v}).",
        "HyStudio ist aktuell (Version {v}).", "HyStudio è aggiornato (versione {v}).",
        "HyStudio обновлён (версия {v}).", "HyStudio 已是最新版本（{v}）。", "HyStudio は最新です（バージョン {v}）。",
        "HyStudio가 최신 버전입니다 (버전 {v})."),
    "Impossible de vérifier les mises à jour : pas de connexion à GitHub.": L(
        "Cannot check for updates: no connection to GitHub.",
        "No se pueden buscar actualizaciones: sin conexión con GitHub.",
        "Updates können nicht geprüft werden: keine Verbindung zu GitHub.",
        "Impossibile cercare aggiornamenti: nessuna connessione a GitHub.",
        "Не удалось проверить обновления: нет соединения с GitHub.",
        "无法检查更新：无法连接 GitHub。", "更新を確認できません：GitHub に接続できません。",
        "업데이트를 확인할 수 없습니다: GitHub에 연결할 수 없습니다."),
    "Le téléchargement de la mise à jour est incomplet ou altéré. Réessayez plus tard.": L(
        "The update download is incomplete or corrupted. Please try again later.",
        "La descarga de la actualización está incompleta o dañada. Inténtelo más tarde.",
        "Der Update-Download ist unvollständig oder beschädigt. Bitte später erneut versuchen.",
        "Il download dell'aggiornamento è incompleto o danneggiato. Riprova più tardi.",
        "Загрузка обновления неполная или повреждена. Повторите попытку позже.",
        "更新下载不完整或已损坏。请稍后重试。", "更新のダウンロードが不完全か破損しています。後でもう一度お試しください。",
        "업데이트 다운로드가 불완전하거나 손상되었습니다. 나중에 다시 시도하세요."),
    "Terminez d'abord le calcul ou la copie en cours.": L(
        "Finish the render or copy in progress first.", "Termine primero el cálculo o la copia en curso.",
        "Beenden Sie zuerst die laufende Berechnung oder Kopie.", "Termina prima il calcolo o la copia in corso.",
        "Сначала дождитесь окончания расчёта или копирования.", "请先完成正在进行的计算或复制。",
        "実行中の計算またはコピーを先に終えてください。", "진행 중인 계산이나 복사를 먼저 끝내세요."),

    # ------------------------------------------------------------ fenetre
    "Prêt": L("Ready", "Listo", "Bereit", "Pronto", "Готово", "就绪", "準備完了", "준비됨"),
    "Vue 3D": L("3D view", "Vista 3D", "3D-Ansicht", "Vista 3D", "3D-вид", "3D 视图", "3D ビュー", "3D 보기"),
    "Aperçu réaliste": L("Realistic preview", "Vista previa realista", "Realistische Vorschau",
                         "Anteprima realistica", "Реалистичный просмотр", "真实预览", "リアルなプレビュー",
                         "사실적 미리보기"),
    "Pièces": L("Parts", "Piezas", "Teile", "Parti", "Детали", "部件", "パーツ", "부품"),
    "Pièce": L("Part", "Pieza", "Teil", "Parte", "Деталь", "部件", "パーツ", "부품"),
    "Triangles": L("Triangles", "Triángulos", "Dreiecke", "Triangoli", "Треугольники", "三角形", "三角形", "삼각형"),
    "Matière": L("Material", "Material", "Material", "Materiale", "Материал", "材质", "マテリアル", "재질"),
    "Studio": L("Studio", "Estudio", "Studio", "Studio", "Студия", "摄影棚", "スタジオ", "스튜디오"),
    "Production": L("Production", "Producción", "Produktion", "Produzione", "Производство", "输出", "出力", "출력"),
    "Filtrer les pièces…": L("Filter parts…", "Filtrar piezas…", "Teile filtern…", "Filtra le parti…",
                             "Фильтр деталей…", "筛选部件…", "パーツを絞り込む…", "부품 필터…"),

    # ------------------------------------------------------------ panneau matiere
    "Cliquez une pièce dans la vue 3D ou dans la liste.": L(
        "Click a part in the 3D view or in the list.", "Haga clic en una pieza en la vista 3D o en la lista.",
        "Klicken Sie auf ein Teil in der 3D-Ansicht oder in der Liste.",
        "Fai clic su una parte nella vista 3D o nell'elenco.", "Щёлкните деталь в 3D-виде или в списке.",
        "在 3D 视图或列表中点击一个部件。", "3D ビューまたはリストでパーツをクリックしてください。",
        "3D 보기나 목록에서 부품을 클릭하세요."),
    "Appliquer à": L("Apply to", "Aplicar a", "Anwenden auf", "Applica a", "Применить к", "应用于", "適用先", "적용 대상"),
    "Cette pièce seulement": L("This part only", "Solo esta pieza", "Nur dieses Teil", "Solo questa parte",
                               "Только эта деталь", "仅此部件", "このパーツのみ", "이 부품만"),
    "Toutes les pièces de ce matériau": L(
        "All parts with this material", "Todas las piezas de este material", "Alle Teile dieses Materials",
        "Tutte le parti di questo materiale", "Все детали из этого материала", "使用此材质的所有部件",
        "このマテリアルのすべてのパーツ", "이 재질의 모든 부품"),
    "Toutes les pièces « {mat} » ({n})": L(
        "All “{mat}” parts ({n})", "Todas las piezas «{mat}» ({n})", "Alle Teile „{mat}“ ({n})",
        "Tutte le parti «{mat}» ({n})", "Все детали «{mat}» ({n})", "所有“{mat}”部件（{n}）",
        "「{mat}」のすべてのパーツ（{n}）", "모든 “{mat}” 부품 ({n})"),
    "nom affiché dans la liste": L("name shown in the list", "nombre mostrado en la lista",
                                   "in der Liste angezeigter Name", "nome mostrato nell'elenco",
                                   "имя в списке", "列表中显示的名称", "リストに表示される名前", "목록에 표시되는 이름"),
    "Nom": L("Name", "Nombre", "Name", "Nome", "Имя", "名称", "名前", "이름"),
    "Rétablir la matière du matériau d'origine": L(
        "Restore the original material", "Restaurar el material original", "Ursprüngliches Material wiederherstellen",
        "Ripristina il materiale originale", "Вернуть исходный материал", "恢复原始材质",
        "元のマテリアルに戻す", "원래 재질로 되돌리기"),
    "Pièce : {name} (matière propre)": L(
        "Part: {name} (own material)", "Pieza: {name} (material propio)", "Teil: {name} (eigenes Material)",
        "Parte: {name} (materiale proprio)", "Деталь: {name} (собственный материал)", "部件：{name}（独立材质）",
        "パーツ：{name}（個別マテリアル）", "부품: {name} (개별 재질)"),
    "Pièce : {name} (hérite de « {mat} »)": L(
        "Part: {name} (inherits “{mat}”)", "Pieza: {name} (hereda de «{mat}»)", "Teil: {name} (erbt von „{mat}“)",
        "Parte: {name} (eredita da «{mat}»)", "Деталь: {name} (наследует «{mat}»)", "部件：{name}（继承“{mat}”）",
        "パーツ：{name}（「{mat}」を継承）", "부품: {name} (“{mat}” 상속)"),
    "Matériau : {mat} — {n} pièce(s)": L(
        "Material: {mat} — {n} part(s)", "Material: {mat} — {n} pieza(s)", "Material: {mat} — {n} Teil(e)",
        "Materiale: {mat} — {n} parte/i", "Материал: {mat} — деталей: {n}", "材质：{mat} — {n} 个部件",
        "マテリアル：{mat} — パーツ {n} 個", "재질: {mat} — 부품 {n}개"),
    "Matériau : {mat}": L("Material: {mat}", "Material: {mat}", "Material: {mat}", "Materiale: {mat}",
                          "Материал: {mat}", "材质：{mat}", "マテリアル：{mat}", "재질: {mat}"),
    "Choisir…": L("Browse…", "Elegir…", "Auswählen…", "Scegli…", "Выбрать…", "选择…", "選択…", "선택…"),
    "Images": L("Images", "Imágenes", "Bilder", "Immagini", "Изображения", "图像", "画像", "이미지"),

    # ------------------------------------------------------------ matieres (core/presets.py)
    "Peinture carrosserie": L("Body paint", "Pintura de carrocería", "Karosserielack", "Vernice carrozzeria",
                              "Краска кузова", "车身漆", "ボディ塗装", "차체 도장"),
    "Chrome": L("Chrome", "Cromo", "Chrom", "Cromo", "Хром", "镀铬", "クローム", "크롬"),
    "Métal": L("Metal", "Metal", "Metall", "Metallo", "Металл", "金属", "金属", "금속"),
    "Plastique": L("Plastic", "Plástico", "Kunststoff", "Plastica", "Пластик", "塑料", "プラスチック", "플라스틱"),
    "Caoutchouc": L("Rubber", "Caucho", "Gummi", "Gomma", "Резина", "橡胶", "ゴム", "고무"),
    "Verre": L("Glass", "Vidrio", "Glas", "Vetro", "Стекло", "玻璃", "ガラス", "유리"),
    "Image (plaque, logo)": L("Image (plate, logo)", "Imagen (matrícula, logotipo)", "Bild (Kennzeichen, Logo)",
                              "Immagine (targa, logo)", "Изображение (номер, логотип)", "图像（车牌、标志）",
                              "画像（ナンバー、ロゴ）", "이미지 (번호판, 로고)"),
    "Masque (invisible)": L("Mask (invisible)", "Máscara (invisible)", "Maske (unsichtbar)",
                            "Maschera (invisibile)", "Маска (невидимая)", "遮罩（不可见）", "マスク（非表示）",
                            "마스크 (보이지 않음)"),
    "Couleur": L("Colour", "Color", "Farbe", "Colore", "Цвет", "颜色", "色", "색상"),
    "Finition": L("Finish", "Acabado", "Oberfläche", "Finitura", "Отделка", "表面", "仕上げ", "마감"),
    "brillant": L("gloss", "brillante", "glänzend", "lucido", "глянец", "亮光", "光沢", "유광"),
    "satiné": L("satin", "satinado", "seidenmatt", "satinato", "сатин", "缎面", "サテン", "새틴"),
    "mat": L("matte", "mate", "matt", "opaco", "мат", "哑光", "マット", "무광"),
    "Réflectance": L("Reflectance", "Reflectancia", "Reflexionsgrad", "Riflettanza", "Отражающая способность",
                     "反射率", "反射率", "반사율"),
    "Poli (0 = miroir)": L("Roughness (0 = mirror)", "Rugosidad (0 = espejo)", "Rauheit (0 = Spiegel)",
                           "Ruvidità (0 = specchio)", "Шероховатость (0 = зеркало)", "粗糙度（0 = 镜面）",
                           "粗さ（0 = 鏡面）", "거칠기 (0 = 거울)"),
    "Rugosité": L("Roughness", "Rugosidad", "Rauheit", "Ruvidità", "Шероховатость", "粗糙度", "粗さ", "거칠기"),
    "Teinte": L("Tint", "Tinte", "Tönung", "Tinta", "Оттенок", "色调", "色合い", "색조"),
    "Transmission par face": L("Transmission per surface", "Transmisión por cara", "Transmission je Fläche",
                               "Trasmissione per faccia", "Пропускание на слой", "每面透光率", "面ごとの透過率",
                               "면당 투과율"),
    "Force du reflet": L("Reflection strength", "Intensidad del reflejo", "Reflexionsstärke",
                         "Intensità del riflesso", "Сила отражения", "反射强度", "反射の強さ", "반사 강도"),
    "Fichier image": L("Image file", "Archivo de imagen", "Bilddatei", "File immagine", "Файл изображения",
                       "图像文件", "画像ファイル", "이미지 파일"),
    "Vernis": L("Clear coat", "Barniz", "Klarlack", "Trasparente", "Лак", "清漆", "クリアコート", "클리어 코트"),

    # ------------------------------------------------------------ autocollant
    "Autocollant": L("Sticker", "Adhesivo", "Aufkleber", "Adesivo", "Наклейка", "贴纸", "ステッカー", "스티커"),
    "Poser une image…": L("Place an image…", "Colocar una imagen…", "Bild platzieren…", "Applica un'immagine…",
                          "Наложить изображение…", "放置图像…", "画像を貼る…", "이미지 붙이기…"),
    "Retirer": L("Remove", "Quitar", "Entfernen", "Rimuovi", "Убрать", "移除", "削除", "제거"),
    "Orienter depuis la vue actuelle": L(
        "Aim from the current view", "Orientar desde la vista actual", "Aus aktueller Ansicht ausrichten",
        "Orienta dalla vista attuale", "Направить по текущему виду", "按当前视角定向",
        "現在の視点から向きを合わせる", "현재 시점에서 방향 맞추기"),
    "Taille": L("Size", "Tamaño", "Größe", "Dimensione", "Размер", "大小", "サイズ", "크기"),
    "Horizontal": L("Horizontal", "Horizontal", "Horizontal", "Orizzontale", "По горизонтали", "水平", "水平", "가로"),
    "Vertical": L("Vertical", "Vertical", "Vertikal", "Verticale", "По вертикали", "垂直", "垂直", "세로"),
    "Rotation": L("Rotation", "Rotación", "Drehung", "Rotazione", "Поворот", "旋转", "回転", "회전"),
    "AUTOCOLLANT_AIDE": L(
        "To place a logo or image here, turn the 3D view to face the spot, then choose the image. "
        "It is laid on top of the material and only shows on the faces turned towards that view.",
        "Para colocar un logotipo o una imagen aquí, gire la vista 3D hacia el lugar deseado y elija la imagen. "
        "Se coloca sobre el material y solo aparece en las caras orientadas hacia esa vista.",
        "Um hier ein Logo oder Bild zu platzieren, drehen Sie die 3D-Ansicht zur gewünschten Stelle und wählen Sie das Bild. "
        "Es liegt über dem Material und erscheint nur auf den Flächen, die dieser Ansicht zugewandt sind.",
        "Per applicare qui un logo o un'immagine, ruota la vista 3D verso il punto desiderato, poi scegli l'immagine. "
        "Si sovrappone al materiale e compare solo sulle facce rivolte verso quella vista.",
        "Чтобы наложить логотип или изображение, поверните 3D-вид к нужному месту и выберите изображение. "
        "Оно ложится поверх материала и видно только на гранях, обращённых к этому виду.",
        "要在此放置标志或图像，请将 3D 视图转到目标位置，然后选择图像。它叠加在材质之上，只显示在朝向该视角的面上。",
        "ロゴや画像を貼るには、3D ビューを貼りたい場所に向けてから画像を選択します。"
        "マテリアルの上に重ねられ、その視点を向いた面にだけ表示されます。",
        "로고나 이미지를 붙이려면 3D 보기를 원하는 위치로 돌린 뒤 이미지를 선택하세요. "
        "재질 위에 겹쳐지며 그 시점을 향한 면에만 표시됩니다.",
        fr="Pour poser un logo ou une image ici : tournez la vue 3D face à l'endroit voulu, puis choisissez l'image. "
           "Elle se pose par-dessus la matière et n'apparaît que sur les faces tournées vers cette vue."),
    "IMAGE_AIDE": L(
        "The image replaces the whole material and is stretched to the part's edges: meant for a flat part "
        "(licence plate). For a logo on the bodywork, keep the real material and add a sticker.",
        "La imagen sustituye todo el material y se estira hasta los bordes de la pieza: pensada para una pieza plana "
        "(matrícula). Para un logotipo en la carrocería, conserve el material real y añada un adhesivo.",
        "Das Bild ersetzt das gesamte Material und wird bis zu den Rändern des Teils gestreckt: gedacht für ein flaches Teil "
        "(Kennzeichen). Für ein Logo auf der Karosserie das echte Material behalten und einen Aufkleber hinzufügen.",
        "L'immagine sostituisce tutto il materiale ed è stirata fino ai bordi della parte: pensata per una parte piatta "
        "(targa). Per un logo sulla carrozzeria, mantieni il materiale reale e aggiungi un adesivo.",
        "Изображение заменяет весь материал и растягивается до краёв детали: подходит для плоской детали "
        "(номерной знак). Для логотипа на кузове оставьте настоящий материал и добавьте наклейку.",
        "图像会替换整个材质并拉伸到部件边缘：适用于平整部件（车牌）。若要在车身上放置标志，请保留原材质并添加贴纸。",
        "画像はマテリアル全体を置き換え、パーツの端まで引き伸ばされます。平らなパーツ（ナンバープレート）向けです。"
        "ボディにロゴを貼るには、元のマテリアルのままステッカーを追加してください。",
        "이미지가 재질 전체를 대체하고 부품 가장자리까지 늘어납니다. 평평한 부품(번호판)용입니다. "
        "차체에 로고를 붙이려면 원래 재질을 유지하고 스티커를 추가하세요.",
        fr="L'image remplace toute la matière et s'étire jusqu'aux bords de la pièce : prévue pour une pièce plate "
           "(plaque). Pour un logo sur la carrosserie, gardez la vraie matière et ajoutez un autocollant."),

    # ------------------------------------------------------------ glTF
    "Matériau d'origine (textures)": L(
        "Original material (textures)", "Material original (texturas)", "Originalmaterial (Texturen)",
        "Materiale originale (texture)", "Исходный материал (текстуры)", "原始材质（纹理）",
        "元のマテリアル（テクスチャ）", "원본 재질 (텍스처)"),
    "Modèles 3D": L("3D models", "Modelos 3D", "3D-Modelle", "Modelli 3D", "3D-модели", "3D 模型",
                    "3D モデル", "3D 모델"),
    "ORIGINE_AIDE": L(
        "The material from the glTF file is used as is, textures included (colours, relief, lights). "
        "Choose another material to replace it.",
        "Se usa tal cual el material del archivo glTF, texturas incluidas (colores, relieve, luces). "
        "Elija otro material para sustituirlo.",
        "Das Material aus der glTF-Datei wird unverändert verwendet, Texturen inbegriffen (Farben, Relief, Leuchten). "
        "Wählen Sie ein anderes Material, um es zu ersetzen.",
        "Il materiale del file glTF è usato così com'è, texture comprese (colori, rilievo, luci). "
        "Scegli un altro materiale per sostituirlo.",
        "Материал из файла glTF используется как есть, вместе с текстурами (цвета, рельеф, подсветка). "
        "Выберите другой материал, чтобы заменить его.",
        "按原样使用 glTF 文件中的材质，包括纹理（颜色、凹凸、发光）。选择其他材质可替换它。",
        "glTF ファイルのマテリアルをテクスチャ（色、凹凸、発光）ごとそのまま使います。置き換えるには別のマテリアルを選んでください。",
        "glTF 파일의 재질을 텍스처(색상, 요철, 발광)까지 그대로 사용합니다. 바꾸려면 다른 재질을 선택하세요.",
        fr="Le matériau du fichier glTF est utilisé tel quel, textures comprises (couleurs, relief, éclairages). "
           "Choisissez une autre matière pour le remplacer."),
    "{n} matériau(x) texturé(s) gardé(s) tels quels (« Matériau d'origine »).": L(
        "{n} textured material(s) kept as is (“Original material”).",
        "{n} material(es) con textura conservado(s) tal cual («Material original»).",
        "{n} texturierte(s) Material(ien) unverändert übernommen („Originalmaterial“).",
        "{n} materiale/i con texture mantenuto/i così com'è («Materiale originale»).",
        "Текстурированных материалов оставлено без изменений: {n} («Исходный материал»).",
        "已按原样保留 {n} 个带纹理的材质（“原始材质”）。",
        "テクスチャ付きマテリアル {n} 個をそのまま使用します（「元のマテリアル」）。",
        "텍스처가 있는 재질 {n}개를 그대로 유지했습니다 (“원본 재질”)."),

    # ------------------------------------------------------------ apercu
    "Vue": L("View", "Vista", "Ansicht", "Vista", "Вид", "视角", "視点", "시점"),
    "{n} échantillons": L("{n} samples", "{n} muestras", "{n} Samples", "{n} campioni", "{n} сэмплов",
                          "{n} 采样", "{n} サンプル", "샘플 {n}개"),
    "Calculer l'aperçu": L("Render preview", "Calcular vista previa", "Vorschau berechnen", "Calcola anteprima",
                           "Рассчитать просмотр", "计算预览", "プレビューを計算", "미리보기 계산"),
    "Rendu Blender d'une vue, tel qu'il apparaîtra sur l'autoradio (800 × 424).": L(
        "Blender render of one view, exactly as the head unit will show it (800 × 424).",
        "Render de Blender de una vista, tal como se verá en la radio del coche (800 × 424).",
        "Blender-Rendering einer Ansicht, genau wie im Autoradio angezeigt (800 × 424).",
        "Render Blender di una vista, come apparirà sull'autoradio (800 × 424).",
        "Рендер Blender одного вида — так, как его покажет магнитола (800 × 424).",
        "Blender 渲染单个视角，与车机上的显示效果一致（800 × 424）。",
        "Blender による 1 視点のレンダリング。カーナビでの表示と同じです（800 × 424）。",
        "Blender로 한 시점을 렌더링합니다. 카오디오에 표시되는 모습 그대로입니다 (800 × 424)."),
    "3/4 avant": L("Front 3/4", "3/4 delantero", "Vorne 3/4", "3/4 anteriore", "Спереди 3/4", "前 3/4",
                   "前方 3/4", "전면 3/4"),
    "Face": L("Front", "Frontal", "Vorne", "Frontale", "Спереди", "正前方", "正面", "정면"),
    "Profil gauche": L("Left side", "Lateral izquierdo", "Linke Seite", "Fianco sinistro", "Слева", "左侧",
                       "左側面", "왼쪽 측면"),
    "3/4 arrière": L("Rear 3/4", "3/4 trasero", "Hinten 3/4", "3/4 posteriore", "Сзади 3/4", "后 3/4",
                     "後方 3/4", "후면 3/4"),
    "Dos": L("Rear", "Trasera", "Hinten", "Posteriore", "Сзади", "正后方", "背面", "후면"),
    "Profil droit": L("Right side", "Lateral derecho", "Rechte Seite", "Fianco destro", "Справа", "右侧",
                      "右側面", "오른쪽 측면"),
    "3/4 avant droit": L("Front right 3/4", "3/4 delantero derecho", "Vorne rechts 3/4", "3/4 anteriore destro",
                         "Спереди справа 3/4", "右前 3/4", "右前方 3/4", "우측 전면 3/4"),
    "Calcul en cours…": L("Rendering…", "Calculando…", "Wird berechnet…", "Calcolo in corso…", "Расчёт…",
                          "正在计算…", "計算中…", "계산 중…"),
    "{view} — calculé en {s} s": L("{view} — rendered in {s} s", "{view} — calculado en {s} s",
                                   "{view} — berechnet in {s} s", "{view} — calcolato in {s} s",
                                   "{view} — рассчитано за {s} с", "{view} — 用时 {s} 秒",
                                   "{view} — {s} 秒で計算", "{view} — {s}초 만에 계산"),
    "Échec de l'aperçu.": L("Preview failed.", "Error en la vista previa.", "Vorschau fehlgeschlagen.",
                            "Anteprima non riuscita.", "Не удалось рассчитать просмотр.", "预览失败。",
                            "プレビューに失敗しました。", "미리보기에 실패했습니다."),

    # ------------------------------------------------------------ studio
    "Exposition": L("Exposure", "Exposición", "Belichtung", "Esposizione", "Экспозиция", "曝光", "露出", "노출"),
    "Netteté": L("Sharpness", "Nitidez", "Schärfe", "Nitidezza", "Резкость", "锐度", "シャープネス", "선명도"),
    "Précision": L("Precision", "Precisión", "Genauigkeit", "Precisione", "Точность", "精度", "精度", "정밀도"),
    "Échantillons": L("Samples", "Muestras", "Samples", "Campioni", "Сэмплы", "采样", "サンプル数", "샘플"),
    "Lumière habitacle": L("Cabin light", "Luz del habitáculo", "Innenraumlicht", "Luce abitacolo",
                           "Свет в салоне", "车内灯光", "室内照明", "실내 조명"),
    " IL": L(" EV", " EV", " LW", " EV", " EV", " EV", " EV", " EV"),
    "{deg}° — {n} vues": L("{deg}° — {n} views", "{deg}° — {n} vistas", "{deg}° — {n} Ansichten",
                           "{deg}° — {n} viste", "{deg}° — {n} видов", "{deg}° — {n} 个视角",
                           "{deg}° — {n} 視点", "{deg}° — {n}개 시점"),
    "Génération ≈ {min} min · fichier ≈ {mb} Mo": L(
        "Generation ≈ {min} min · file ≈ {mb} MB", "Generación ≈ {min} min · archivo ≈ {mb} MB",
        "Erzeugung ≈ {min} min · Datei ≈ {mb} MB", "Generazione ≈ {min} min · file ≈ {mb} MB",
        "Генерация ≈ {min} мин · файл ≈ {mb} МБ", "生成 ≈ {min} 分钟 · 文件 ≈ {mb} MB",
        "生成 ≈ {min} 分 · ファイル ≈ {mb} MB", "생성 ≈ {min}분 · 파일 ≈ {mb} MB"),
    "⚠ plus de la moitié de la mémoire libre de l'autoradio (280 Mo)": L(
        "⚠ more than half of the head unit's free memory (280 MB)",
        "⚠ más de la mitad de la memoria libre de la radio (280 MB)",
        "⚠ mehr als die Hälfte des freien Autoradio-Speichers (280 MB)",
        "⚠ più della metà della memoria libera dell'autoradio (280 MB)",
        "⚠ больше половины свободной памяти магнитолы (280 МБ)",
        "⚠ 超过车机可用内存的一半（280 MB）", "⚠ カーナビの空きメモリ（280 MB）の半分以上",
        "⚠ 카오디오 여유 메모리(280 MB)의 절반 이상"),

    # ------------------------------------------------------------ production
    "Générer pour l'autoradio": L("Generate for the head unit", "Generar para la radio", "Für das Autoradio erzeugen",
                                  "Genera per l'autoradio", "Создать для магнитолы", "为车机生成",
                                  "カーナビ用に生成", "카오디오용 생성"),
    "Interrompre": L("Cancel", "Cancelar", "Abbrechen", "Interrompi", "Прервать", "中止", "中止", "중단", fr="Annuler"),
    "Copier sur la carte SD": L("Copy to SD card", "Copiar a la tarjeta SD", "Auf SD-Karte kopieren",
                                "Copia sulla scheda SD", "Копировать на SD-карту", "复制到 SD 卡",
                                "SD カードにコピー", "SD 카드에 복사"),
    "Aucune génération en cours.": L("No generation in progress.", "Ninguna generación en curso.",
                                     "Keine Erzeugung aktiv.", "Nessuna generazione in corso.",
                                     "Генерация не выполняется.", "当前没有生成任务。", "生成は実行されていません。",
                                     "진행 중인 생성이 없습니다."),
    "Fichier pour l'autoradio": L("File for the head unit", "Archivo para la radio", "Datei für das Autoradio",
                                  "File per l'autoradio", "Файл для магнитолы", "车机文件", "カーナビ用ファイル",
                                  "카오디오용 파일"),
    "Vues i20view": L("i20view views", "Vistas i20view", "i20view-Ansichten", "Viste i20view", "Виды i20view",
                      "i20view 视角文件", "i20view ビュー", "i20view 시점 파일"),
    "Génération de {n} vues vers {path}": L(
        "Generating {n} views to {path}", "Generando {n} vistas en {path}", "Erzeuge {n} Ansichten nach {path}",
        "Generazione di {n} viste in {path}", "Генерация {n} видов в {path}", "正在生成 {n} 个视角到 {path}",
        "{n} 視点を {path} に生成中", "{n}개 시점을 {path}에 생성 중"),
    "{d} / {t} vues — reste {min} min — fin vers {end}": L(
        "{d} / {t} views — {min} min left — done around {end}",
        "{d} / {t} vistas — quedan {min} min — fin hacia las {end}",
        "{d} / {t} Ansichten — noch {min} min — fertig gegen {end}",
        "{d} / {t} viste — mancano {min} min — fine verso le {end}",
        "{d} / {t} видов — осталось {min} мин — окончание около {end}",
        "{d} / {t} 个视角 — 剩余 {min} 分钟 — 预计 {end} 完成",
        "{d} / {t} 視点 — 残り {min} 分 — {end} ごろ完了",
        "{d} / {t} 시점 — {min}분 남음 — {end}경 완료"),
    "Terminé : {mb} Mo en {min} min.": L(
        "Done: {mb} MB in {min} min.", "Terminado: {mb} MB en {min} min.", "Fertig: {mb} MB in {min} min.",
        "Completato: {mb} MB in {min} min.", "Готово: {mb} МБ за {min} мин.", "完成：{mb} MB，用时 {min} 分钟。",
        "完了：{mb} MB、{min} 分。", "완료: {mb} MB, {min}분 소요."),
    "Fichier prêt : {path} ({mb} Mo)": L(
        "File ready: {path} ({mb} MB)", "Archivo listo: {path} ({mb} MB)", "Datei bereit: {path} ({mb} MB)",
        "File pronto: {path} ({mb} MB)", "Файл готов: {path} ({mb} МБ)", "文件已就绪：{path}（{mb} MB）",
        "ファイル準備完了：{path}（{mb} MB）", "파일 준비 완료: {path} ({mb} MB)"),
    "Génération interrompue — aucun fichier écrit.": L(
        "Generation stopped — no file written.", "Generación interrumpida: no se ha escrito ningún archivo.",
        "Erzeugung abgebrochen — keine Datei geschrieben.", "Generazione interrotta — nessun file scritto.",
        "Генерация прервана — файл не записан.", "生成已中止 — 未写入文件。",
        "生成を中止しました — ファイルは書き込まれていません。", "생성이 중단되었습니다 — 파일을 쓰지 않았습니다."),
    "Génération en cours": L("Generation in progress", "Generación en curso", "Erzeugung läuft",
                             "Generazione in corso", "Идёт генерация", "正在生成", "生成中", "생성 중"),
    "Une génération est en cours. L'arrêter et quitter ?": L(
        "A generation is in progress. Stop it and quit?", "Hay una generación en curso. ¿Detenerla y salir?",
        "Eine Erzeugung läuft. Abbrechen und beenden?", "È in corso una generazione. Interromperla e uscire?",
        "Идёт генерация. Остановить и выйти?", "正在生成。要停止并退出吗？", "生成中です。中止して終了しますか？",
        "생성이 진행 중입니다. 중단하고 끝낼까요?"),

    # ------------------------------------------------------------ projet
    "Profil i20 validé créé : {path}": L(
        "Validated i20 profile created: {path}", "Perfil i20 validado creado: {path}",
        "Validiertes i20-Profil erstellt: {path}", "Profilo i20 validato creato: {path}",
        "Создан проверенный профиль i20: {path}", "已创建已验证的 i20 配置：{path}",
        "検証済み i20 プロファイルを作成しました：{path}", "검증된 i20 프로필을 만들었습니다: {path}"),
    "Modèle introuvable": L("Model not found", "Modelo no encontrado", "Modell nicht gefunden",
                            "Modello non trovato", "Модель не найдена", "找不到模型", "モデルが見つかりません",
                            "모델을 찾을 수 없음"),
    "Le modèle du projet est introuvable :\n{path}": L(
        "The project's model cannot be found:\n{path}", "No se encuentra el modelo del proyecto:\n{path}",
        "Das Modell des Projekts wurde nicht gefunden:\n{path}", "Il modello del progetto non è stato trovato:\n{path}",
        "Модель проекта не найдена:\n{path}", "找不到项目的模型：\n{path}",
        "プロジェクトのモデルが見つかりません：\n{path}", "프로젝트의 모델을 찾을 수 없습니다:\n{path}"),
    "Chargement du modèle {name}…": L(
        "Loading model {name}…", "Cargando el modelo {name}…", "Modell {name} wird geladen…",
        "Caricamento del modello {name}…", "Загрузка модели {name}…", "正在加载模型 {name}…",
        "モデル {name} を読み込み中…", "모델 {name} 불러오는 중…"),
    "Chargement": L("Loading", "Carga", "Laden", "Caricamento", "Загрузка", "加载", "読み込み", "불러오기"),
    "{parts} pièces, {tris} triangles": L(
        "{parts} parts, {tris} triangles", "{parts} piezas, {tris} triángulos", "{parts} Teile, {tris} Dreiecke",
        "{parts} parti, {tris} triangoli", "Деталей: {parts}, треугольников: {tris}", "{parts} 个部件，{tris} 个三角形",
        "パーツ {parts} 個、三角形 {tris} 個", "부품 {parts}개, 삼각형 {tris}개"),
    "Modèle non découpé en pièces": L(
        "Model not split into parts", "Modelo no dividido en piezas", "Modell nicht in Teile zerlegt",
        "Modello non suddiviso in parti", "Модель не разделена на детали", "模型未拆分为部件",
        "モデルがパーツに分割されていません", "모델이 부품으로 나뉘어 있지 않음"),
    "NON_DECOUPE": L(
        "“{name}” does not split the vehicle into parts: the whole model is a single object.\n\n"
        "Still available:\n"
        "  • edit materials per material (list on the left, or click in the 3D view),\n"
        "  • hide a material,\n"
        "  • preview, generation and copy to the SD card.\n\n"
        "Not supported with this file:\n"
        "  • selecting and editing a single part,\n"
        "  • placing an image (plate, logo) on a part.\n\n"
        "To use them, export the model with one object per part (“objects” or “groups” option of the OBJ export).",
        "«{name}» no separa el vehículo en piezas: todo el modelo es un único objeto.\n\n"
        "Sigue disponible:\n"
        "  • modificar los materiales por material (lista de la izquierda o clic en la vista 3D),\n"
        "  • ocultar un material,\n"
        "  • vista previa, generación y copia a la tarjeta SD.\n\n"
        "No compatible con este archivo:\n"
        "  • seleccionar y modificar una sola pieza,\n"
        "  • colocar una imagen (matrícula, logotipo) en una pieza.\n\n"
        "Para usarlas, exporte el modelo con un objeto por pieza (opción «objetos» o «grupos» de la exportación OBJ).",
        "„{name}“ zerlegt das Fahrzeug nicht in Teile: Das ganze Modell ist ein einziges Objekt.\n\n"
        "Weiterhin verfügbar:\n"
        "  • Materialien pro Material ändern (Liste links oder Klick in der 3D-Ansicht),\n"
        "  • ein Material ausblenden,\n"
        "  • Vorschau, Erzeugung und Kopie auf die SD-Karte.\n\n"
        "Mit dieser Datei nicht möglich:\n"
        "  • ein einzelnes Teil auswählen und ändern,\n"
        "  • ein Bild (Kennzeichen, Logo) auf ein Teil legen.\n\n"
        "Exportieren Sie dafür das Modell mit einem Objekt pro Teil (Option „Objekte“ oder „Gruppen“ beim OBJ-Export).",
        "«{name}» non separa il veicolo in parti: l'intero modello è un unico oggetto.\n\n"
        "Sempre disponibile:\n"
        "  • modificare i materiali per materiale (elenco a sinistra o clic nella vista 3D),\n"
        "  • nascondere un materiale,\n"
        "  • anteprima, generazione e copia sulla scheda SD.\n\n"
        "Non supportato con questo file:\n"
        "  • selezionare e modificare una singola parte,\n"
        "  • applicare un'immagine (targa, logo) a una parte.\n\n"
        "Per usarle, esporta il modello con un oggetto per parte (opzione «oggetti» o «gruppi» dell'esportazione OBJ).",
        "«{name}» не разделяет автомобиль на детали: вся модель — один объект.\n\n"
        "Доступно:\n"
        "  • изменение материалов по материалу (список слева или щелчок в 3D-виде),\n"
        "  • скрытие материала,\n"
        "  • просмотр, генерация и копирование на SD-карту.\n\n"
        "Недоступно с этим файлом:\n"
        "  • выбор и изменение отдельной детали,\n"
        "  • наложение изображения (номер, логотип) на деталь.\n\n"
        "Чтобы пользоваться ими, экспортируйте модель с отдельным объектом для каждой детали "
        "(параметр «объекты» или «группы» при экспорте OBJ).",
        "“{name}”没有将车辆拆分为部件：整个模型是一个对象。\n\n"
        "仍可使用：\n"
        "  • 按材质修改材质（左侧列表，或在 3D 视图中点击），\n"
        "  • 隐藏某个材质，\n"
        "  • 预览、生成和复制到 SD 卡。\n\n"
        "此文件不支持：\n"
        "  • 选择并修改单个部件，\n"
        "  • 在部件上放置图像（车牌、标志）。\n\n"
        "如需使用，请以每个部件一个对象的方式导出模型（OBJ 导出的“对象”或“组”选项）。",
        "「{name}」は車両をパーツに分割していません。モデル全体が 1 つのオブジェクトです。\n\n"
        "引き続き使用できる機能：\n"
        "  • マテリアル単位での変更（左のリスト、または 3D ビューでクリック）\n"
        "  • マテリアルの非表示\n"
        "  • プレビュー、生成、SD カードへのコピー\n\n"
        "このファイルでは使用できない機能：\n"
        "  • 単一パーツの選択と変更\n"
        "  • パーツへの画像（ナンバー、ロゴ）の貼り付け\n\n"
        "使用するには、パーツごとに 1 つのオブジェクトでモデルをエクスポートしてください"
        "（OBJ エクスポートの「オブジェクト」または「グループ」オプション）。",
        "“{name}” 파일은 차량을 부품으로 나누지 않습니다. 모델 전체가 하나의 개체입니다.\n\n"
        "계속 사용 가능:\n"
        "  • 재질별 재질 변경 (왼쪽 목록 또는 3D 보기에서 클릭),\n"
        "  • 재질 숨기기,\n"
        "  • 미리보기, 생성, SD 카드로 복사.\n\n"
        "이 파일에서는 지원되지 않음:\n"
        "  • 단일 부품 선택 및 변경,\n"
        "  • 부품에 이미지(번호판, 로고) 붙이기.\n\n"
        "사용하려면 부품마다 개체 하나로 모델을 내보내세요 (OBJ 내보내기의 “개체” 또는 “그룹” 옵션).",
        fr="« {name} » ne sépare pas le véhicule en pièces : tout le modèle forme un seul objet.\n\n"
           "Toujours disponible :\n"
           "  • modifier les matières par matériau (liste de gauche, ou clic dans la vue 3D),\n"
           "  • masquer un matériau,\n"
           "  • aperçu, génération et copie sur la carte SD.\n\n"
           "Non pris en charge avec ce fichier :\n"
           "  • sélectionner et modifier une pièce seule,\n"
           "  • poser une image (plaque, logo) sur une pièce.\n\n"
           "Pour en profiter, exportez le modèle avec un objet par pièce "
           "(option « objets » ou « groupes » de l'export OBJ)."),
    "Modèle 3D": L("3D model", "Modelo 3D", "3D-Modell", "Modello 3D", "3D-модель", "3D 模型", "3D モデル", "3D 모델"),
    "Projets HyStudio": L("HyStudio projects", "Proyectos HyStudio", "HyStudio-Projekte", "Progetti HyStudio",
                          "Проекты HyStudio", "HyStudio 项目", "HyStudio プロジェクト", "HyStudio 프로젝트"),
    "Enregistrer le projet": L("Save project", "Guardar proyecto", "Projekt speichern", "Salva progetto",
                               "Сохранить проект", "保存项目", "プロジェクトを保存", "프로젝트 저장"),
    "Ouvrir un projet": L("Open project", "Abrir proyecto", "Projekt öffnen", "Apri progetto", "Открыть проект",
                          "打开项目", "プロジェクトを開く", "프로젝트 열기"),
    "Ouverture": L("Open", "Apertura", "Öffnen", "Apertura", "Открытие", "打开", "開く", "열기"),
    "Enregistrer sous": L("Save as", "Guardar como", "Speichern unter", "Salva con nome", "Сохранить как",
                          "另存为", "名前を付けて保存", "다른 이름으로 저장"),
    "Projet enregistré : {path}": L(
        "Project saved: {path}", "Proyecto guardado: {path}", "Projekt gespeichert: {path}",
        "Progetto salvato: {path}", "Проект сохранён: {path}", "项目已保存：{path}",
        "プロジェクトを保存しました：{path}", "프로젝트를 저장했습니다: {path}"),
    "Modifications non enregistrées": L(
        "Unsaved changes", "Cambios sin guardar", "Nicht gespeicherte Änderungen", "Modifiche non salvate",
        "Несохранённые изменения", "未保存的更改", "未保存の変更", "저장하지 않은 변경 사항"),
    "Enregistrer les modifications du projet ?": L(
        "Save changes to the project?", "¿Guardar los cambios del proyecto?", "Änderungen am Projekt speichern?",
        "Salvare le modifiche al progetto?", "Сохранить изменения проекта?", "保存对项目的更改吗？",
        "プロジェクトの変更を保存しますか？", "프로젝트 변경 사항을 저장할까요?"),
    "{path} n'est pas un projet HyStudio": L(
        "{path} is not a HyStudio project", "{path} no es un proyecto HyStudio", "{path} ist kein HyStudio-Projekt",
        "{path} non è un progetto HyStudio", "{path} не является проектом HyStudio", "{path} 不是 HyStudio 项目",
        "{path} は HyStudio プロジェクトではありません", "{path}은(는) HyStudio 프로젝트가 아닙니다"),

    # ------------------------------------------------------------ fichier MTL
    "Importer les matériaux d'un fichier MTL…": L(
        "Import materials from an MTL file…", "Importar materiales de un archivo MTL…",
        "Materialien aus MTL-Datei importieren…", "Importa materiali da un file MTL…",
        "Импортировать материалы из файла MTL…", "从 MTL 文件导入材质…",
        "MTL ファイルからマテリアルを読み込む…", "MTL 파일에서 재질 가져오기…"),
    "Fichier de matériaux": L("Materials file", "Archivo de materiales", "Materialdatei", "File dei materiali",
                              "Файл материалов", "材质文件", "マテリアルファイル", "재질 파일"),
    "Matériaux MTL": L("MTL materials", "Materiales MTL", "MTL-Materialien", "Materiali MTL", "Материалы MTL",
                       "MTL 材质", "MTL マテリアル", "MTL 재질"),
    "Utiliser le MTL": L("Use the MTL", "Usar el MTL", "MTL verwenden", "Usa l'MTL", "Использовать MTL",
                         "使用 MTL", "MTL を使用", "MTL 사용"),
    "Ignorer": L("Ignore", "Ignorar", "Ignorieren", "Ignora", "Пропустить", "忽略", "無視", "무시"),
    "MTL_QUESTION": L(
        "The model comes with the materials file “{file}”.\n\n"
        "{n} of its {total} materials have usable colours, transparency or reflections. "
        "Use them as starting materials?\n\n"
        "Otherwise, materials are guessed from their names. You can also import this file later (File menu).",
        "El modelo incluye el archivo de materiales «{file}».\n\n"
        "{n} de sus {total} materiales tienen colores, transparencias o reflejos aprovechables. "
        "¿Usarlos como materiales iniciales?\n\n"
        "Si no, los materiales se deducen de sus nombres. También puede importar este archivo más tarde (menú Archivo).",
        "Zum Modell gehört die Materialdatei „{file}“.\n\n"
        "{n} von {total} Materialien haben verwertbare Farben, Transparenzen oder Reflexionen. "
        "Als Ausgangsmaterialien übernehmen?\n\n"
        "Andernfalls werden die Materialien anhand ihrer Namen erraten. Sie können die Datei auch später importieren (Menü Datei).",
        "Il modello è accompagnato dal file dei materiali «{file}».\n\n"
        "{n} dei suoi {total} materiali hanno colori, trasparenze o riflessi utilizzabili. "
        "Usarli come materiali di partenza?\n\n"
        "Altrimenti i materiali vengono dedotti dai nomi. Puoi anche importare il file più tardi (menu File).",
        "К модели прилагается файл материалов «{file}».\n\n"
        "У {n} из {total} материалов есть пригодные цвета, прозрачность или отражения. "
        "Использовать их как исходные материалы?\n\n"
        "Иначе материалы определяются по названиям. Файл можно импортировать и позже (меню «Файл»).",
        "模型附带材质文件“{file}”。\n\n"
        "其 {total} 个材质中有 {n} 个包含可用的颜色、透明度或反射。要将其用作初始材质吗？\n\n"
        "否则将根据材质名称推测。之后也可以导入此文件（文件菜单）。",
        "モデルにはマテリアルファイル「{file}」が付属しています。\n\n"
        "{total} 個のマテリアルのうち {n} 個に、使用できる色・透明度・反射があります。初期マテリアルとして使用しますか？\n\n"
        "使用しない場合は、名前からマテリアルを推定します。このファイルは後から読み込むこともできます（ファイル メニュー）。",
        "모델에 재질 파일 “{file}”이(가) 함께 있습니다.\n\n"
        "{total}개 재질 중 {n}개에 사용할 수 있는 색상, 투명도 또는 반사 값이 있습니다. 시작 재질로 사용할까요?\n\n"
        "사용하지 않으면 이름으로 재질을 추정합니다. 이 파일은 나중에 가져올 수도 있습니다 (파일 메뉴).",
        fr="Le modèle est accompagné du fichier de matériaux « {file} ».\n\n"
           "{n} matériau(x) sur {total} y ont des couleurs, transparences ou reflets exploitables. "
           "Les reprendre comme matières de départ ?\n\n"
           "Sinon, les matières sont devinées d'après les noms des matériaux. "
           "Vous pourrez aussi importer ce fichier plus tard (menu Fichier)."),
    "« {file} » ignoré : il ne contient que les valeurs par défaut de l'exportateur.": L(
        "“{file}” ignored: it only contains the exporter's default values.",
        "«{file}» ignorado: solo contiene los valores predeterminados del exportador.",
        "„{file}“ ignoriert: enthält nur die Standardwerte des Exporters.",
        "«{file}» ignorato: contiene solo i valori predefiniti dell'esportatore.",
        "«{file}» пропущен: в нём только значения экспортёра по умолчанию.",
        "已忽略“{file}”：其中只有导出程序的默认值。",
        "「{file}」は無視しました：エクスポーターの既定値しか含まれていません。",
        "“{file}” 무시됨: 내보내기 프로그램의 기본값만 들어 있습니다."),
    "MTL_DEFAUTS": L(
        "“{file}” only contains the exporter's default values (uniform grey): nothing to import.",
        "«{file}» solo contiene los valores predeterminados del exportador (gris uniforme): nada que importar.",
        "„{file}“ enthält nur die Standardwerte des Exporters (einheitliches Grau): nichts zu importieren.",
        "«{file}» contiene solo i valori predefiniti dell'esportatore (grigio uniforme): niente da importare.",
        "В «{file}» только значения экспортёра по умолчанию (однородный серый): импортировать нечего.",
        "“{file}”只包含导出程序的默认值（统一灰色）：没有可导入的内容。",
        "「{file}」にはエクスポーターの既定値（一様なグレー）しかありません。読み込むものはありません。",
        "“{file}”에는 내보내기 프로그램의 기본값(균일한 회색)만 있습니다. 가져올 내용이 없습니다.",
        fr="« {file} » ne contient que les valeurs par défaut de l'exportateur (gris uniforme) : rien à importer."),
    "MTL_AUCUN": L(
        "No material in “{file}” matches the model's materials.",
        "Ningún material de «{file}» coincide con los del modelo.",
        "Kein Material aus „{file}“ passt zu den Materialien des Modells.",
        "Nessun materiale di «{file}» corrisponde a quelli del modello.",
        "Ни один материал из «{file}» не совпадает с материалами модели.",
        "“{file}”中没有与模型材质相符的材质。",
        "「{file}」にはモデルのマテリアルと一致するものがありません。",
        "“{file}”에 모델의 재질과 일치하는 재질이 없습니다.",
        fr="Aucun matériau de « {file} » ne correspond à ceux du modèle."),
    "MTL_IMPORT": L(
        "Replace the materials of {n} material(s) with the values from “{file}”?\n\n"
        "Parts with their own material are not changed. Ctrl+Z undoes the import.",
        "¿Reemplazar los materiales de {n} material(es) por los valores de «{file}»?\n\n"
        "Las piezas con material propio no cambian. Ctrl+Z deshace la importación.",
        "Materialien von {n} Material(ien) durch die Werte aus „{file}“ ersetzen?\n\n"
        "Teile mit eigenem Material bleiben unverändert. Strg+Z macht den Import rückgängig.",
        "Sostituire i materiali di {n} materiale/i con i valori di «{file}»?\n\n"
        "Le parti con un materiale proprio non cambiano. Ctrl+Z annulla l'importazione.",
        "Заменить материалы ({n}) значениями из «{file}»?\n\n"
        "Детали с собственным материалом не изменятся. Ctrl+Z отменяет импорт.",
        "要用“{file}”中的值替换 {n} 个材质吗？\n\n"
        "拥有独立材质的部件不会改变。Ctrl+Z 可撤销导入。",
        "{n} 個のマテリアルを「{file}」の値で置き換えますか？\n\n"
        "個別マテリアルを持つパーツは変更されません。Ctrl+Z で読み込みを元に戻せます。",
        "재질 {n}개를 “{file}”의 값으로 바꿀까요?\n\n"
        "개별 재질이 있는 부품은 바뀌지 않습니다. Ctrl+Z로 가져오기를 취소할 수 있습니다.",
        fr="Remplacer les matières de {n} matériau(x) par les valeurs de « {file} » ?\n\n"
           "Les pièces qui ont une matière propre ne changent pas. Ctrl+Z annule l'import."),
    "Matières importées depuis « {file} » : {n} matériau(x).": L(
        "Materials imported from “{file}”: {n} material(s).",
        "Materiales importados de «{file}»: {n} material(es).",
        "Materialien aus „{file}“ importiert: {n} Material(ien).",
        "Materiali importati da «{file}»: {n} materiale/i.",
        "Материалы импортированы из «{file}»: {n}.",
        "已从“{file}”导入材质：{n} 个。",
        "「{file}」からマテリアルを読み込みました：{n} 個。",
        "“{file}”에서 재질을 가져왔습니다: {n}개."),

    "Projet converti au format .hysp : {path}": L(
        "Project converted to the .hysp format: {path}", "Proyecto convertido al formato .hysp: {path}",
        "Projekt in das .hysp-Format umgewandelt: {path}", "Progetto convertito nel formato .hysp: {path}",
        "Проект преобразован в формат .hysp: {path}", "项目已转换为 .hysp 格式：{path}",
        "プロジェクトを .hysp 形式に変換しました：{path}", "프로젝트를 .hysp 형식으로 변환했습니다: {path}"),
    "Ouvrez un projet ou créez-en un depuis un modèle 3D (menu Fichier).": L(
        "Open a project or create one from a 3D model (File menu).",
        "Abra un proyecto o cree uno a partir de un modelo 3D (menú Archivo).",
        "Öffnen Sie ein Projekt oder erstellen Sie eines aus einem 3D-Modell (Menü Datei).",
        "Apri un progetto o creane uno da un modello 3D (menu File).",
        "Откройте проект или создайте его из 3D-модели (меню «Файл»).",
        "打开项目，或从 3D 模型新建项目（文件菜单）。",
        "プロジェクトを開くか、3D モデルから作成してください（ファイル メニュー）。",
        "프로젝트를 열거나 3D 모델로 새로 만드세요 (파일 메뉴)."),

    # ------------------------------------------------------------ carte SD
    "Fichier de vues à copier": L("Views file to copy", "Archivo de vistas para copiar", "Zu kopierende Ansichtsdatei",
                                  "File di viste da copiare", "Файл видов для копирования", "要复制的视角文件",
                                  "コピーするビューファイル", "복사할 시점 파일"),
    "Carte SD": L("SD card", "Tarjeta SD", "SD-Karte", "Scheda SD", "SD-карта", "SD 卡", "SD カード", "SD 카드"),
    "Aucune carte SD de l'autoradio détectée.\nBranchez-la (elle contient eu20_upgrade.lgu) puis réessayez.": L(
        "No head unit SD card detected.\nInsert it (it contains eu20_upgrade.lgu) and try again.",
        "No se ha detectado la tarjeta SD de la radio.\nInsértela (contiene eu20_upgrade.lgu) y vuelva a intentarlo.",
        "Keine SD-Karte des Autoradios erkannt.\nStecken Sie sie ein (sie enthält eu20_upgrade.lgu) und versuchen Sie es erneut.",
        "Nessuna scheda SD dell'autoradio rilevata.\nInseriscila (contiene eu20_upgrade.lgu) e riprova.",
        "SD-карта магнитолы не найдена.\nВставьте её (на ней есть eu20_upgrade.lgu) и повторите попытку.",
        "未检测到车机的 SD 卡。\n请插入（其中包含 eu20_upgrade.lgu）后重试。",
        "カーナビの SD カードが見つかりません。\n挿入して（eu20_upgrade.lgu が入っています）もう一度お試しください。",
        "카오디오 SD 카드가 감지되지 않았습니다.\n카드를 넣고(eu20_upgrade.lgu 포함) 다시 시도하세요."),
    "Carte SD non intègre": L("SD card not clean", "Tarjeta SD dañada", "SD-Karte fehlerhaft", "Scheda SD non integra",
                              "SD-карта повреждена", "SD 卡不完整", "SD カードに不整合があります", "SD 카드 오류"),
    "SD_SALE": L(
        "The volume {root} is marked as not clean (power cut during a write).\n"
        "Repair it first: right-click the drive > Properties > Tools > Check,\n"
        "or run “chkdsk {drive} /f” as administrator.",
        "El volumen {root} está marcado como dañado (corte durante una escritura).\n"
        "Repárelo primero: clic derecho en la unidad > Propiedades > Herramientas > Comprobar,\n"
        "o «chkdsk {drive} /f» como administrador.",
        "Das Laufwerk {root} ist als fehlerhaft markiert (Stromausfall beim Schreiben).\n"
        "Reparieren Sie es zuerst: Rechtsklick auf das Laufwerk > Eigenschaften > Tools > Prüfen,\n"
        "oder „chkdsk {drive} /f“ als Administrator.",
        "Il volume {root} è segnato come non integro (interruzione durante una scrittura).\n"
        "Riparalo prima: clic destro sull'unità > Proprietà > Strumenti > Controlla,\n"
        "oppure «chkdsk {drive} /f» come amministratore.",
        "Том {root} помечен как повреждённый (отключение во время записи).\n"
        "Сначала исправьте его: правый щелчок по диску > Свойства > Сервис > Проверить,\n"
        "или «chkdsk {drive} /f» от имени администратора.",
        "卷 {root} 被标记为不完整（写入时断电）。\n"
        "请先修复：右键单击驱动器 > 属性 > 工具 > 检查，\n"
        "或以管理员身份运行“chkdsk {drive} /f”。",
        "ボリューム {root} は不整合としてマークされています（書き込み中の電源断）。\n"
        "先に修復してください：ドライブを右クリック > プロパティ > ツール > チェック、\n"
        "または管理者として「chkdsk {drive} /f」を実行します。",
        "볼륨 {root}이(가) 오류로 표시되어 있습니다 (쓰기 중 전원 차단).\n"
        "먼저 복구하세요: 드라이브 오른쪽 클릭 > 속성 > 도구 > 검사,\n"
        "또는 관리자 권한으로 “chkdsk {drive} /f” 실행.",
        fr="Le volume {root} est marqué non intègre (coupure pendant une écriture).\n"
           "Réparez-le d'abord : clic droit sur le lecteur > Propriétés > Outils > Vérifier,\n"
           "ou « chkdsk {drive} /f » en administrateur."),
    "Copie sur {root}…": L("Copying to {root}…", "Copiando a {root}…", "Kopiere nach {root}…",
                           "Copia su {root}…", "Копирование на {root}…", "正在复制到 {root}…",
                           "{root} にコピー中…", "{root}에 복사 중…"),
    "Copie vérifiée (MD5) : {files}": L(
        "Copy verified (MD5): {files}", "Copia verificada (MD5): {files}", "Kopie geprüft (MD5): {files}",
        "Copia verificata (MD5): {files}", "Копия проверена (MD5): {files}", "复制已校验（MD5）：{files}",
        "コピーを検証しました（MD5）：{files}", "복사 검증 완료 (MD5): {files}"),
    "Carte éjectée, vous pouvez la retirer.": L(
        "Card ejected, you can remove it.", "Tarjeta expulsada, ya puede retirarla.",
        "Karte ausgeworfen, Sie können sie entnehmen.", "Scheda espulsa, puoi rimuoverla.",
        "Карта извлечена, её можно вынуть.", "SD 卡已弹出，可以取出。", "カードを取り出しました。抜いてかまいません。",
        "카드를 꺼냈습니다. 이제 분리해도 됩니다."),
    "Copie faite. Éjectez la carte avant de la retirer.": L(
        "Copy done. Eject the card before removing it.", "Copia hecha. Expulse la tarjeta antes de retirarla.",
        "Kopie fertig. Werfen Sie die Karte vor dem Entnehmen aus.", "Copia completata. Espelli la scheda prima di rimuoverla.",
        "Копирование завершено. Извлеките карту перед тем, как вынуть её.", "复制完成。取出前请先弹出 SD 卡。",
        "コピーが完了しました。抜く前にカードを取り出してください。", "복사 완료. 분리하기 전에 카드를 꺼내세요."),
    "Copie": L("Copy", "Copia", "Kopieren", "Copia", "Копирование", "复制", "コピー", "복사"),
    "Copie corrompue sur {dst} (MD5 {got} au lieu de {want})": L(
        "Corrupted copy on {dst} (MD5 {got} instead of {want})", "Copia dañada en {dst} (MD5 {got} en lugar de {want})",
        "Beschädigte Kopie auf {dst} (MD5 {got} statt {want})", "Copia danneggiata su {dst} (MD5 {got} invece di {want})",
        "Повреждённая копия на {dst} (MD5 {got} вместо {want})", "{dst} 上的副本已损坏（MD5 为 {got}，应为 {want}）",
        "{dst} のコピーが破損しています（MD5 {got}、正しくは {want}）", "{dst}의 복사본 손상 (MD5 {got}, 예상 {want})"),

    # ------------------------------------------------------------ Blender (core/pipeline.py)
    "Blender introuvable (dossier tools/ du dépôt ou Program Files)": L(
        "Blender not found (tools/ folder of the repository or Program Files)",
        "Blender no encontrado (carpeta tools/ del repositorio o Program Files)",
        "Blender nicht gefunden (Ordner tools/ des Repositorys oder Program Files)",
        "Blender non trovato (cartella tools/ del repository o Program Files)",
        "Blender не найден (папка tools/ репозитория или Program Files)",
        "找不到 Blender（仓库的 tools/ 文件夹或 Program Files）",
        "Blender が見つかりません（リポジトリの tools/ フォルダーまたは Program Files）",
        "Blender를 찾을 수 없습니다 (저장소의 tools/ 폴더 또는 Program Files)"),
    "Le rendu a échoué : voir {log}": L(
        "Render failed: see {log}", "El render ha fallado: ver {log}", "Rendering fehlgeschlagen: siehe {log}",
        "Il render non è riuscito: vedi {log}", "Рендер не удался: см. {log}", "渲染失败：请查看 {log}",
        "レンダリングに失敗しました：{log} を参照", "렌더링 실패: {log} 참조"),
    "Blender s'est arrêté à la vue {i} : voir {log}": L(
        "Blender stopped at view {i}: see {log}", "Blender se detuvo en la vista {i}: ver {log}",
        "Blender hat bei Ansicht {i} angehalten: siehe {log}", "Blender si è fermato alla vista {i}: vedi {log}",
        "Blender остановился на виде {i}: см. {log}", "Blender 在第 {i} 个视角停止：请查看 {log}",
        "Blender が視点 {i} で停止しました：{log} を参照", "Blender가 시점 {i}에서 멈췄습니다: {log} 참조"),

    # ------------------------------------------------------------ noms du profil i20 (core/project.py)
    "Plastiques noirs et toit": L("Black plastics and roof", "Plásticos negros y techo", "Schwarze Kunststoffe und Dach",
                                  "Plastiche nere e tetto", "Чёрный пластик и крыша", "黑色塑料件和车顶",
                                  "黒い樹脂パーツとルーフ", "검은색 플라스틱과 지붕"),
    "Chromes et optiques": L("Chrome and lights", "Cromados y ópticas", "Chrom und Leuchten", "Cromature e fari",
                             "Хром и оптика", "镀铬件和灯组", "クロームとライト", "크롬과 램프"),
    "Vitres": L("Windows", "Cristales", "Scheiben", "Vetri", "Стёкла", "车窗", "窓ガラス", "창유리"),
    "Optiques transparentes": L("Clear lenses", "Ópticas transparentes", "Klare Leuchtengläser", "Fari trasparenti",
                                "Прозрачная оптика", "透明灯罩", "透明レンズ", "투명 렌즈"),
    "Feux rouges": L("Red lights", "Luces rojas", "Rote Leuchten", "Luci rosse", "Красные фонари", "红色灯",
                     "赤いライト", "빨간 램프"),
    "Clignotants": L("Indicators", "Intermitentes", "Blinker", "Frecce", "Поворотники", "转向灯", "ウインカー",
                     "방향지시등"),
    "Habitacle": L("Interior", "Habitáculo", "Innenraum", "Abitacolo", "Салон", "车内", "室内", "실내"),
    "Pneus": L("Tyres", "Neumáticos", "Reifen", "Pneumatici", "Шины", "轮胎", "タイヤ", "타이어"),
    "Jantes (clair)": L("Rims (light)", "Llantas (claro)", "Felgen (hell)", "Cerchi (chiaro)", "Диски (светлые)",
                        "轮毂（浅色）", "ホイール（明）", "휠 (밝은색)"),
    "Jantes (foncé)": L("Rims (dark)", "Llantas (oscuro)", "Felgen (dunkel)", "Cerchi (scuro)", "Диски (тёмные)",
                        "轮毂（深色）", "ホイール（暗）", "휠 (어두운색)"),
    "Disques de frein": L("Brake discs", "Discos de freno", "Bremsscheiben", "Dischi dei freni", "Тормозные диски",
                          "刹车盘", "ブレーキディスク", "브레이크 디스크"),
    "Miroirs des rétroviseurs": L("Mirror glass", "Espejos de los retrovisores", "Spiegelgläser",
                                  "Specchi dei retrovisori", "Зеркала", "后视镜镜面", "ミラー面", "사이드미러 거울"),
    "Plaques d'immatriculation": L("Licence plates", "Matrículas", "Kennzeichen", "Targhe", "Номерные знаки",
                                   "车牌", "ナンバープレート", "번호판"),
    "Toit ouvrant": L("Sunroof", "Techo solar", "Schiebedach", "Tetto apribile", "Люк", "天窗", "サンルーフ", "선루프"),
    "Logo H arrière": L("Rear H logo", "Logotipo H trasero", "H-Logo hinten", "Logo H posteriore",
                        "Задний логотип H", "后部 H 标志", "リアの H ロゴ", "후면 H 로고"),
    "Inscription HYUNDAI": L("HYUNDAI lettering", "Letras HYUNDAI", "HYUNDAI-Schriftzug", "Scritta HYUNDAI",
                             "Надпись HYUNDAI", "HYUNDAI 字标", "HYUNDAI エンブレム", "HYUNDAI 레터링"),
    "Inscription HYUNDAI (point)": L("HYUNDAI lettering (dot)", "Letras HYUNDAI (punto)", "HYUNDAI-Schriftzug (Punkt)",
                                     "Scritta HYUNDAI (punto)", "Надпись HYUNDAI (точка)", "HYUNDAI 字标（点）",
                                     "HYUNDAI エンブレム（点）", "HYUNDAI 레터링 (점)"),
    "Monogramme i20": L("i20 badge", "Anagrama i20", "i20-Schriftzug", "Sigla i20", "Шильдик i20", "i20 字标",
                        "i20 エンブレム", "i20 엠블럼"),
    "Plaque avant": L("Front plate", "Matrícula delantera", "Kennzeichen vorne", "Targa anteriore",
                      "Передний номер", "前车牌", "フロントナンバー", "앞 번호판"),
    "Plaque arrière": L("Rear plate", "Matrícula trasera", "Kennzeichen hinten", "Targa posteriore",
                        "Задний номер", "后车牌", "リアナンバー", "뒤 번호판"),
}
