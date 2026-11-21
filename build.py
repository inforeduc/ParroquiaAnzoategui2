import re, html, json, sys

SRC_PATH = '/mnt/user-data/attachments/1225eede-cc38-502c-ab84-4747a9e46294/d49d5e6a-attachment.txt'
OUT_PATH = '/tmp/claude-0/-home-claude/1225eede-cc38-502c-ab84-4747a9e46294/scratchpad/anzoategui.html'

SRC = open(SRC_PATH, encoding='utf-8').read().split('\n')

def raw(n):
    return SRC[n - 1]

FIX = [
    ('Orto antecedente', 'Otro antecedente'),
    ('Motesinos', 'Montesinos'),
    ('podernos nombrar', 'podemos nombrar'),
    ('q ue', 'que'),
    ('extiende n', 'extienden'),
    ('Cosuelo', 'Consuelo'),
    ('que tubo sobre', 'que tuvo sobre'),
    ('tubo entre sus defensores', 'tuvo entre sus defensores'),
    ('relazándose', 'realizándose'),
    ('impertención', 'hipertensión'),
    ('la perdida de la identidad', 'la pérdida de la identidad'),
    ('mubles', 'muebles'),
    ('microhistiriadores', 'microhistoriadores'),
    ('abesto', 'asbesto'),
    ('Cienaga', 'Ciénaga'),
    ('Ciénaga”', 'Ciénaga”'),
]

def clean(s):
    s = s.replace('\t', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    for a, b in FIX:
        s = s.replace(a, b)
    s = html.escape(s, quote=False)
    s = re.sub(r'\s*[….]{5,}\s*', ' HUECO ', s)
    s = re.sub(r'_{2,}', 'HUECO', s)
    s = re.sub(r'(HUECO[\s,.]*){2,}', 'HUECO ', s)
    s = s.replace('HUECO', '<span class="hueco" title="Espacio en blanco en el texto original">[…]</span>')
    return s.strip()

def strip_dash(t):
    return re.sub(r'^[-•]\s*', '', t.strip()).strip()

def rng(a, b, quotes=(), skip=()):
    out, ul = [], []
    def flush():
        nonlocal ul
        if ul:
            out.append('<ul>' + ''.join(f'<li>{i}</li>' for i in ul) + '</ul>')
            ul = []
    for n in range(a, b + 1):
        if n in skip:
            continue
        t = raw(n).strip()
        if not t:
            continue
        if re.match(r'^[-•]', t):
            item = strip_dash(t)
            if item:
                ul.append(clean(item))
            continue
        flush()
        t = re.sub(r'^\.\s+', '', t)
        if n in quotes:
            out.append(f'<blockquote><p>{clean(t)}</p></blockquote>')
        else:
            out.append(f'<p>{clean(t)}</p>')
    flush()
    return '\n'.join(out)

def P(n):
    return f'<p>{clean(re.sub(r"^\.\s+", "", raw(n).strip()))}</p>'

def olist(a, b):
    items = []
    for n in range(a, b + 1):
        t = raw(n).strip()
        m = re.match(r'^\d+\.\s*(.*)$', t)
        if m:
            items.append(clean(m.group(1)))
    return '<ol class="num">' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'

def ulist(items, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<ul{c}>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'

def dl_lines(lines, drop_por=True):
    rows = []
    for n in lines:
        t = strip_dash(raw(n))
        if ':' not in t:
            continue
        k, v = t.split(':', 1)
        k = re.sub(r'^Por el\s+', '', k.strip())
        v = v.strip().rstrip('.')
        rows.append(f'<div><dt>{clean(k)}</dt><dd>{clean(v)}</dd></div>')
    return '<dl class="limites">' + ''.join(rows) + '</dl>'

def stat(num, label):
    return f'<div class="stat"><b>{num}</b><span>{label}</span></div>'

def stats(items):
    return '<div class="stats">' + ''.join(stat(a, b) for a, b in items) + '</div>'

def small_list(a, b):
    items = []
    for n in range(a, b + 1):
        t = raw(n).strip()
        if not t:
            continue
        t = strip_dash(t)
        if t.endswith('.') and not t.endswith(').'):
            t = t[:-1]
        elif t.endswith(').'):
            t = t[:-1]
        items.append(clean(t))
    return items

# ------------------------------------------------------------------ pages
PAGES = {}
ORDER = []

def page(pid, title, body):
    PAGES[pid] = (title, body)
    ORDER.append(pid)

# ===== Proyecto
page('introduccion', 'Introducción', rng(24, 29))

page('justificacion', 'Justificación, contexto y diagnóstico', rng(47, 53) + '''
<aside class="callout"><b>Para ver el contexto y el diagnóstico en detalle</b>
<p>Los datos de la parroquia están organizados en el menú <a href="#historia">La parroquia</a>: historia, ubicación, población, servicios, economía, recreación y los <a href="#diagnostico">problemas detectados en el diagnóstico participativo</a>. Las manifestaciones culturales están en el menú <a href="#casa-cultura">Cultura y tradiciones</a>.</p></aside>''')

page('antecedentes', 'Antecedentes', rng(234, 239))

page('fundamentacion', 'Fundamentación teórica y referentes', rng(268, 315, quotes={271, 276, 284, 291, 295, 305}))

page('objetivos', 'Objetivos del proyecto',
     '<h2>Objetivo general</h2>' + P(340) +
     '<h2>Objetivos específicos</h2>' + olist(343, 347) +
     '<h2>Objetivos de aprendizaje</h2>' + rng(355, 363))

page('metodologia', 'Aspectos metodológicos', rng(391, 404))

# ===== Parroquia
HISTORIA_TL = [
    ('Antes de 1600', 'Francisco de San Juan, uno de los 59 hombres que fundaron El Tocuyo, es el encomendero de “La Ciénaga”.'),
    ('1601–1606', 'La encomienda “La Ciénaga” es otorgada a Diego Betancourt.'),
    ('1620', 'El Gobernador Don Francisco de la Hoz Berrío funda el pueblo de Guarico. “La Ciénaga” queda como ejido de esa población.'),
    ('1620–1856', 'El nombre oficial se mantiene como “La Ciénaga” durante 236 años.'),
    ('1845', 'El hacendado Juan Linarez dona sus tierras para crear el curato en devoción a la Virgen del Rosario.'),
    ('8 dic 1856', 'Se nombra por primera vez Municipio Anzoátegui, durante el gobierno del General José Tadeo Monagas, en honor al General José Antonio Anzoátegui. El ejecútese es del 19 de diciembre y se realiza en enero de 1857.'),
    ('Jul 1859', 'La Diputación de Barquisimeto elimina el Municipio por decreto.'),
    ('Dic 1864', 'La Ley territorial de Barquisimeto lo restablece.'),
    ('1989', 'Pasa de Municipio Anzoátegui a Parroquia Anzoátegui por la Ley de Reforma Parcial y la Ley de Demarcaciones Políticas Territoriales.'),
]
tl = '<ol class="timeline">' + ''.join(f'<li><time>{d}</time><p>{t}</p></li>' for d, t in HISTORIA_TL) + '</ol>'
page('historia', 'Historia: de La Ciénaga a Parroquia',
     '<h2>Cronología resumida</h2>' + tl + '<h2>El relato completo</h2>' + rng(54, 66))

# ubicación
t73 = clean(raw(73))
parts = re.split(r'(?=Existe una gran diversidad|Cuenta con una vegetación|El relieve y el clima|Su fauna es variada)', t73)
heads = ['Extensión y relieve', 'Suelos y posición astronómica', 'Vegetación', 'Hidrografía', 'Fauna']
geo = ''.join(f'<h3>{h}</h3><p>{p.strip()}</p>' for h, p in zip(heads, parts))
page('ubicacion', 'Ubicación y geografía',
     stats([('1.780 m', 'altitud sobre el nivel del mar'), ('35 km²', 'extensión'), ('40 km', 'desde El Tocuyo, capital del Municipio Morán')]) +
     P(67) + '<h2>Límites de la parroquia</h2>' + dl_lines([68, 69, 70, 71]) +
     '<h2>Medio físico y naturaleza</h2>' + geo)

CASERIOS = ['El Rodeo', 'Sabana Grande', 'Los Membrillos', 'Agua Turbia', 'Potrero de la Virgen', 'Sanarito',
            'La Boca', 'La Trinidad', 'El Almorzadero', 'Quebrada de Oro', 'La Ceiba', 'Cerro Gordo']
page('poblacion', 'Población y caseríos',
     stats([('8.308', 'habitantes en la parroquia'), ('12', 'caseríos alrededor del pueblo'), ('28', 'consejos comunales')]) +
     P(74) + '<h2>Los caseríos</h2>' +
     '<ul class="chips">' + ''.join(f'<li>{c}</li>' for c in CASERIOS) + '</ul>' +
     '<h2>Participación comunitaria</h2>' + P(115))

AGES = [('0 a 12 años · niños', 263), ('13 a 17 años · jóvenes', 68), ('18 a 59 años', 111), ('60 a 97 años · ancianos', 56)]
bars = '<div class="bars" role="list" aria-label="Habitantes del pueblo por edad">' + ''.join(
    f'<div class="bar-row" role="listitem"><span class="bl">{l}</span><span class="bt"><i style="width:{n / 498 * 100:.1f}%"></i></span><span class="bn">{n}</span></div>'
    for l, n in AGES) + '</div>'
page('pueblo', 'El pueblo de Anzoátegui',
     '<p class="lead">' + clean(raw(75)) + '</p>' +
     stats([('498', 'habitantes'), ('198', 'viviendas'), ('12', 'viviendas con piso de tierra')]) +
     '<h2>Límites</h2>' + dl_lines([77, 78, 79, 80]) +
     '<h2>Habitantes</h2>' + P(84) + bars +
     '<h2>Viviendas</h2>' + P(85) + P(86))

# salud y educación
t96 = clean(raw(96))
seg_pae = t96.index('Funciona en esta institución')
seg_rural = t96.index('En todos los Caseríos')
seg_mis = t96.index('Asimismo, contamos con')
seg_rib = t96.index('y la Misión Ribas')
p_matricula = t96[:seg_pae].strip()
p_pae = t96[seg_pae:seg_rural].strip()
p_rural = t96[seg_rural:seg_mis].strip()
mis_intro = 'Asimismo, contamos con las siguientes misiones educativas:'
mis_text = t96[seg_mis + len(mis_intro):].strip()
rob_i = mis_text.index('La Misión')
rob = mis_text[rob_i:seg_rib - seg_mis - len(mis_intro) - 0].strip() if False else None
body_mis = t96[seg_mis + len(mis_intro):seg_rib].strip() + '.'
body_rib = ('La ' + t96[seg_rib + 5:]).strip() if t96[seg_rib + 5:].startswith('Misión') else t96[seg_rib + 2:].strip()

page('salud-educacion', 'Salud y educación',
     '<h2>Salud</h2>' + P(87) +
     '<h2>Educación</h2>' + P(88) +
     '<div class="callout etimo"><b>Zazarabicoa</b><p><span class="term">Zazara</span> = Arena &nbsp;·&nbsp; <span class="term">Coa</span> = Agua</p></div>' +
     '<h3>Cronología de la institución</h3>' +
     '<ol class="timeline">' +
     '<li><time>1946</time><p>Fundación con el nombre de Escuela Federal Rural “Zazarabicoa”. Su primer maestro y director fue Silvio Agüero, con un primer grado de 14 alumnos.</p></li>' +
     '<li><time>1950–1951</time><p>Primera promoción de 6º grado, con cuatro alumnos graduandos.</p></li>' +
     '<li><time>1975–1976</time><p>Inicia el preescolar, siendo directora la maestra Consuelo Orellana y docente a cargo la maestra Gladys Linarez.</p></li>' +
     '<li><time>1991–1992</time><p>Se inicia el 7.º grado bajo la dirección de Nelson Peroza, y luego 8.º y 9.º. La primera promoción Básica es en 1994.</p></li>' +
     '<li><time>2000–2001</time><p>Se logra el primer año diversificado y, al año siguiente, el 2.º año, siendo director encargado Crispiliano Escalona. La primera promoción de Bachilleres Mención Ciencias es en 2002, con 27 alumnos.</p></li>' +
     '<li><time>2002</time><p>Inicia como Escuela Bolivariana y se crea el aula integrada (A.I.) para atender a niños, niñas y adolescentes con dificultad de aprendizaje.</p></li>' +
     '</ol>' +
     '<h3>La institución hoy</h3>' +
     stats([('571', 'alumnos'), ('337', 'en Educación Inicial y Primaria'), ('234', 'en Educación Secundaria'), ('35', 'docentes')]) +
     f'<p>{p_matricula}</p><p>{p_pae}</p><p>{p_rural}</p>' +
     '<h3>Misiones educativas</h3>' +
     f'<p>{mis_intro}</p>' +
     f'<div class="cards2"><article class="card"><h4>Misión Robinson</h4><p>{body_mis}</p></article>' +
     f'<article class="card"><h4>Misión Ribas</h4><p>{body_rib}</p></article></div>')

serv_inst = ['Jefatura Civil', 'Puesto Policial', 'Junta Parroquial', 'Iglesia Nuestra Señora del Rosario', 'Plaza Bolívar',
             'Casa de la Cultura “Ricardo Peraza”', 'Gimnasio “Zulma de Melo”', 'Estadio “José Antonio Castillo”',
             'Parque Bolsillo', 'Centro de Gestión Parroquial',
             'Hogar de Cuidado Diario: atiende a parte de los niños no escolarizados, por no tener la edad correspondiente para entrar a la escuela',
             'Un expendio de medicinas']
serv_com = ['Una bodega Mercal', 'Una librería', '11 bodegas', 'Una quincalla', 'Una panadería', '01 siver',
            'Seis expendios de licores legales', 'Cuatro expendios de licores ilegales']
serv_srv = ['Transporte público (rapiditos y autobuses)', 'Telefonía fija y celular', 'Sistema de cloacas', 'Servicio de electricidad',
            'Agua potable', 'Televisión por cable', '03 teléfonos públicos de C.A.N.T.V.', 'Servicio de aseo urbano']
page('servicios', 'Instituciones y servicios',
     '<p>Están presentes en la comunidad las siguientes instituciones, comercios y servicios.</p>'
     '<div class="cards3">'
     '<article class="card"><h3>Instituciones y espacios</h3>' + ulist(serv_inst) + '</article>'
     '<article class="card"><h3>Comercios</h3>' + ulist(serv_com) + '</article>'
     '<article class="card"><h3>Servicios</h3>' + ulist(serv_srv) + '</article>'
     '</div>')

HOR = [('4:00 a. m.', '7:00 a. m.'), ('7:00 a. m.', '10:00 a. m.'), ('12:00 m.', '3:00 p. m.'), ('2:30 p. m.', '5:00 p. m.')]
page('vialidad', 'Vialidad y transporte',
     '<h2>La vía principal</h2>' + P(81) + P(82) +
     '<h2>Autobuses a Barquisimeto</h2>' + P(100) +
     '<div class="tablewrap"><table><caption class="sr">Horarios de autobuses entre Anzoátegui y Barquisimeto</caption>'
     '<thead><tr><th scope="col">Sale de Anzoátegui hacia Barquisimeto</th><th scope="col">Sale de Barquisimeto hacia Anzoátegui</th></tr></thead><tbody>' +
     ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in HOR) + '</tbody></table></div>')

page('economia', 'Economía y comercio',
     '<h2>Actividad económica</h2>' + P(99) +
     '<p class="chips-label">Cultivos que más se producen</p><ul class="chips"><li>Café</li><li>Papa</li><li>Maíz</li><li>Tomate</li><li>Pimentón</li></ul>' +
     '<h2>Comercio</h2>' + rng(168, 170))

page('recursos', 'Recursos de la comunidad',
     '<div class="cards2"><article class="card"><h3>Recursos naturales</h3>' + ulist(small_list(107, 108)) + '</article>'
     '<article class="card"><h3>Recursos humanos</h3>' + ulist(small_list(110, 112)) + '</article></div>'
     '<h2>Contexto político</h2>' + P(115))

page('recreacion', 'Recreación y deporte',
     '<h2>Recreación y deporte</h2>' + P(173) +
     '<h2>Sitios de esparcimiento</h2>' + ulist(small_list(177, 184)) +
     '<h2>Intercambios deportivos</h2>' + P(187) + P(189))

PROB_LABELS = ['Agua potable', 'Vivienda', 'Educación', 'Vialidad', 'Identidad cultural', 'Valores familiares y comunitarios',
               'Salud', 'Enfermedades frecuentes', 'Pobreza y empleo', 'Contaminación ambiental', 'Reforestación', 'Calidad del aire']
probs = []
for i, n in enumerate(range(194, 206)):
    probs.append(f'<li><b>{PROB_LABELS[i]}</b><p>{clean(strip_dash(raw(n)))}</p></li>')
page('diagnostico', 'Problemas y debilidades',
     '<p class="lead">' + clean(raw(192)) + '</p><ol class="probs">' + ''.join(probs) + '</ol>')

# ===== Cultura
page('casa-cultura', 'Casa de la Cultura, tradiciones e himno',
     '<h2>La Casa de la Cultura “Ricardo Peraza”</h2>' + P(118) + P(119) +
     '<h2>Tradiciones culturales</h2>' + P(122) +
     '<h2>El himno de la parroquia</h2>' + P(123) +
     stats([('1995–1996', 'año en que se funda el himno'), ('7 jun 1998', 'oficialización en acto protocolar')]) +
     '<div class="cards2"><article class="card"><h4>Letra</h4><p>Prof. Antonio Gutiérrez</p></article><article class="card"><h4>Música</h4><p>Prof. Rafael Pargas</p></article></div>')

cal_rows = []
for n in range(128, 136):
    t = clean(strip_dash(raw(n)))
    if ' – ' in t:
        d, e = t.split(' – ', 1)
        cal_rows.append((d.strip(), e.strip().rstrip('.')))
page('calendario', 'Calendario de manifestaciones',
     '<p>' + clean(raw(127)) + '</p>'
     '<div class="tablewrap"><table><caption class="sr">Calendario de manifestaciones culturales</caption><thead><tr><th scope="col">Fecha</th><th scope="col">Manifestación</th></tr></thead><tbody>' +
     ''.join(f'<tr><td>{d}</td><td>{e}</td></tr>' for d, e in cal_rows) + '</tbody></table></div>' +
     '<aside class="callout"><b>Manifestaciones que el proyecto busca rescatar</b><p>Se pretenden rescatar las ' + clean(raw(50)).split('Con el desarrollo del presente proyecto se pretenden rescatar las', 1)[-1].strip() + '</p></aside>')

page('gastronomia', 'Gastronomía',
     '<div class="cards3">'
     '<article class="card"><h3>Platos típicos</h3>' + ulist(small_list(139, 144)) + '</article>'
     '<article class="card"><h3>Dulces</h3>' + ulist(small_list(147, 152)) + '</article>'
     '<article class="card"><h3>Bebidas</h3>' + ulist(small_list(155, 158)) + '</article></div>')

page('mitos', 'Mitos, leyendas y creencias',
     ulist(small_list(161, 166), 'big') +
     '<p class="note">Las leyendas y creencias recogidas en las entrevistas aparecen en <a href="#personajes">Personajes populares</a> (la leyenda del Bajío, los espantos de las loas) y los rituales en <a href="#salve">La Salve a la Virgen del Carmen</a>.</p>')

# ===== Experiencia
page('descripcion', 'Descripción de la experiencia',
     P(433) + P(435) + P(445) +
     '<h2>Recorrido por las actividades</h2>'
     '<div class="cards2">'
     '<a class="card link" href="#salve"><h4>La Salve a la Virgen del Carmen</h4><p>La velada en casa del Sr. Régulo Báez.</p></a>'
     '<a class="card link" href="#personajes"><h4>Personajes populares</h4><p>Las entrevistas a cultores, músicos, rezanderos y curanderas.</p></a>'
     '<a class="card link" href="#actividades"><h4>Actividades del plan de acción</h4><p>Viacrucis, taller de títeres, obra de teatro y folleto.</p></a>'
     '<a class="card link" href="#incidencia"><h4>Incidencia en la comunidad</h4><p>Qué cambió con el proyecto.</p></a>'
     '</div>')

page('salve', 'La Salve a la Virgen del Carmen', rng(437, 443))

PERS = [
    ('Régulo Báez', 'Paga promesas a la Virgen del Carmen; salve desde 1985'),
    ('Pedro Escalona', 'Dirige los cantores de salve y el grupo “Los Cincuentones”. Patrimonio Viviente'),
    ('Rafael Pargas', 'Profesor. Patrimonio Viviente del Municipio Morán. Música del himno'),
    ('Mireya Peraza', 'Diseña los vestidos de la Virgen del Rosario desde hace más de 20 años'),
    ('Guillermo Antonio Villegas', 'Músico empírico; grupo Los Ritmos de Anzoátegui'),
    ('Rafael Ángel Gómez', 'Único Bailador de Batalla que queda en la comunidad'),
    ('Inginio Vizcaya', 'Rezandero por más de 50 años; tiene 86 años'),
    ('José “Cheo” Vizcaya', 'Cantor de velorios y salves; realiza posturas de agua'),
    ('Clemente José Pérez', 'Compone y cuenta loas'),
    ('Elauteria Cedeño', 'Conocedora del uso medicinal de las plantas'),
    ('Juana Vargas', 'Tiene el don de curar la culebrilla'),
    ('Bartolo y Adriana de Pérez', 'Rezanderos de novenarios, misas de difuntos y velorios'),
    ('Reinaldo Terán', 'Tallador empírico de madera'),
    ('Consuelo Orellana', 'Maestra, directora de la Escuela Zazarabicoa por más de 15 años (difunta)'),
    ('Ricardo Peraza', 'Licenciado nacido en Anzoátegui; la Casa de la Cultura lleva su nombre'),
]
pers_grid = '<ul class="people">' + ''.join(f'<li><b>{n}</b><span>{r}</span></li>' for n, r in PERS) + '</ul>'

def acc(title, sub, body, open_=False):
    o = ' open' if open_ else ''
    return f'<details{o}><summary><span class="st">{title}</span><span class="ss">{sub}</span></summary><div class="dbody">{body}</div></details>'

tools = '<div class="tools"><button type="button" data-expand="all">Expandir todo</button><button type="button" data-expand="none">Contraer todo</button></div>'

page('personajes', 'Personajes populares',
     '<p>' + clean(raw(445)).split('Las áreas')[0] + '</p>' if False else
     '<p>Las entrevistas a los personajes populares fueron la fuente principal de la historia local. Aquí están quienes aparecen en el texto y, más abajo, el relato completo de cada visita.</p>' +
     '<h2>Quién es quién</h2>' + pers_grid +
     '<h2>Las entrevistas</h2>' + tools +
     acc('Mireya Peraza', 'Diseñadora de los vestidos de la Virgen del Rosario', rng(447, 448)) +
     acc('Guillermo Antonio Villegas', 'Músico empírico y narrador de leyendas', rng(450, 456)) +
     acc('Rafael Ángel', 'Bailador de Batalla', rng(458, 458)) +
     acc('Inginio Vizcaya y familia', 'Rezandero, posturas de agua y objetos tradicionales', rng(460, 462)) +
     acc('Clemente José Pérez', 'Las loas y el baile “La Bamba”', rng(464, 466)) +
     acc('Elauteria Cedeño', 'Plantas medicinales', rng(468, 470)))

page('actividades', 'Actividades del plan de acción',
     '<h2>El Viacrucis del Sector El Calvario</h2>' + P(472) +
     '<h2>Taller de títeres</h2>' + P(474) +
     '<h2>Obra de teatro con títeres</h2>' + P(476) + P(478) + P(479) + P(480) +
     '<h2>Conversatorios y folleto</h2>' + P(482))

page('incidencia', 'Incidencia en la comunidad', rng(488, 497))

# ===== Aprendizajes
def title_case(s):
    small = {'y', 'de', 'la', 'el', 'los', 'las', 'del', 'en', 'como', 'desde', 'su'}
    words = s.lower().split(' ')
    out = []
    for i, w in enumerate(words):
        out.append(w if (i > 0 and w in small) else w[:1].upper() + w[1:])
    return ' '.join(out)

ejes = []
cur = None
state = None
for n in range(514, 752):
    t = raw(n).strip()
    if not t:
        continue
    m = re.match(r'^(\d+)\.-\s*Eje Tem[aá]tico:\s*(.+?)\s*\.?$', t)
    if m:
        cur = {'n': m.group(1), 't': m.group(2), 'areas': [], 'aprend': [], 'narr': []}
        if cur['t'].isupper():
            cur['t'] = title_case(cur['t'])
        ejes.append(cur)
        state = None
        continue
    if cur is None:
        continue
    if t.startswith('Áreas de Conocimientos Referenciales'):
        state = 'areas'
        continue
    if t.startswith('Aprendizajes Adquiridos'):
        state = 'aprend'
        continue
    if state == 'areas':
        cur['areas'].append(clean(strip_dash(t)))
    elif state == 'aprend':
        if re.match(r'^[-•]', t):
            cur['aprend'].append(clean(strip_dash(t)))
        else:
            cur['narr'].append(clean(t))

assert len(ejes) == 16, len(ejes)
eje_html = tools
for e in ejes:
    body = '<div class="eje-cols"><div><h4>Áreas de conocimiento referencial</h4>' + ulist(e['areas']) + '</div>' \
           '<div><h4>Aprendizajes adquiridos</h4>' + ulist(e['aprend']) + '</div></div>'
    if e['narr']:
        body += '<h4>Cómo se desarrolló en el proyecto</h4>' + ''.join(f'<p>{p}</p>' for p in e['narr'])
    eje_html += acc(f'Eje {e["n"]}', e['t'], body)

page('ejes', 'Ejes temáticos y aprendizajes',
     '<p>' + clean(raw(512)) + '</p>' + eje_html)

page('habilidades', 'Habilidades y destrezas', rng(776, 809).replace('<ul>', '<ul class="cols">', 1))

vals = []
for n in range(818, 831):
    t = raw(n).strip()
    if not t:
        continue
    t = clean(strip_dash(t))
    if ': ' in t:
        k, v = t.split(': ', 1)
        vals.append(f'<li><b>{k}</b><p>{v}</p></li>')
    else:
        vals.append(f'<li><p>{t}</p></li>')
page('valores', 'Valores y actitudes', '<ul class="vals">' + ''.join(vals) + '</ul>')

# ===== Cierre
page('conclusiones', 'Conclusiones y consideraciones generales', rng(837, 844))
page('recomendaciones', 'Recomendaciones', P(845) + olist(847, 853))

anexos = '<ul class="anexos">' + ''.join(
    f'<li><span class="ph" aria-hidden="true"></span><b>Anexo N.º {i}</b></li>' for i in range(1, 22)) + '</ul>'
page('anexos', 'Anexos',
     '<p>El informe original incluye 21 anexos con el material fotográfico y documental del proyecto: entrevistas, la salve, el altar, los vestidos de la Virgen, el taller y la obra de títeres, el guion y el folleto. En el texto recibido figuran solo los encabezados, por lo que aquí quedan los espacios listos para sumar las imágenes.</p>' + anexos)

GROUPS = [
    ('proyecto', 'El proyecto', ['introduccion', 'justificacion', 'antecedentes', 'fundamentacion', 'objetivos', 'metodologia']),
    ('parroquia', 'La parroquia', ['historia', 'ubicacion', 'poblacion', 'pueblo', 'salud-educacion', 'servicios', 'vialidad', 'economia', 'recursos', 'recreacion', 'diagnostico']),
    ('cultura', 'Cultura y tradiciones', ['casa-cultura', 'calendario', 'gastronomia', 'mitos']),
    ('experiencia', 'Experiencia y personajes', ['descripcion', 'salve', 'personajes', 'actividades', 'incidencia']),
    ('aprendizajes', 'Aprendizajes', ['ejes', 'habilidades', 'valores']),
    ('cierre', 'Cierre', ['conclusiones', 'recomendaciones', 'anexos']),
]
flat = [p for _, _, ids in GROUPS for p in ids]
assert set(flat) == set(PAGES), set(PAGES) ^ set(flat)

menu = [{'id': gid, 'title': gt, 'items': [{'id': p, 'title': PAGES[p][0]} for p in ids]} for gid, gt, ids in GROUPS]
group_of = {p: gt for _, gt, ids in GROUPS for p in ids}

# ------------------------------------------------------------------ home
home_cards = ''.join(
    f'<section class="hcard"><h3>{gt}</h3><ul>' + ''.join(f'<li><a href="#{p}">{PAGES[p][0]}</a></li>' for p in ids) + '</ul></section>'
    for _, gt, ids in GROUPS)

RIDGE = '''<svg class="ridge" viewBox="0 0 1200 170" preserveAspectRatio="none" aria-hidden="true" focusable="false">
<path class="r1" d="M0 110 L90 70 L170 98 L280 40 L380 90 L470 58 L580 104 L700 36 L800 84 L910 52 L1010 96 L1110 64 L1200 92 V170 H0Z"/>
<path class="r2" d="M0 132 L110 96 L210 122 L330 78 L440 120 L560 88 L670 126 L790 82 L900 118 L1020 90 L1120 120 L1200 104 V170 H0Z"/>
<path class="r3" d="M0 152 L130 126 L260 148 L400 116 L540 146 L690 120 L830 148 L980 124 L1100 146 L1200 134 V170 H0Z"/>
</svg>'''

home = f'''
<div class="hero">
  <div class="hero-in">
    <p class="eyebrow">Parroquia Anzoátegui · Municipio Morán · Estado Lara</p>
    <h1>Anzoátegui, antes La Ciénaga</h1>
    <p class="proj">“La difusión de la historia local, como estrategia de acción para el reconocimiento de los valores culturales de la comunidad de Anzoátegui, parroquia Anzoátegui, municipio Morán, estado Lara”</p>
    <div class="hero-cta"><a class="btn" href="#introduccion">Comenzar por la introducción</a><a class="btn ghost" href="#historia">Ver la historia</a></div>
  </div>
  {RIDGE}
</div>
<div class="home-body">
{stats([('1.780 m', 'sobre el nivel del mar'), ('35 km²', 'de extensión'), ('8.308', 'habitantes en la parroquia'), ('28', 'consejos comunales'), ('236 años', 'llamada “La Ciénaga” (1620–1856)')])}
<h2>Explora el sitio</h2>
<p class="sub">Toda la información del proyecto está en estos seis menús. También puedes usar la búsqueda de la parte superior.</p>
<div class="hgrid">{home_cards}</div>
</div>
'''

pages_html = f'<section class="page" id="p-inicio" data-id="inicio" data-title="Inicio" data-group="">{home}</section>\n'
for pid in flat:
    title, body = PAGES[pid]
    pages_html += (f'<section class="page" id="p-{pid}" data-id="{pid}" data-title="{html.escape(title)}" data-group="{group_of[pid]}">'
                   f'<div class="doc"><header class="phead"><p class="crumb"><a href="#inicio">Inicio</a> <span aria-hidden="true">›</span> {group_of[pid]}</p>'
                   f'<h1 tabindex="-1">{title}</h1></header><div class="prose">{body}</div></div></section>\n')

TEMPLATE = open('/tmp/claude-0/-home-claude/1225eede-cc38-502c-ab84-4747a9e46294/scratchpad/template.html', encoding='utf-8').read()
out = TEMPLATE.replace('%%PAGES%%', pages_html).replace('%%MENU%%', json.dumps(menu, ensure_ascii=False)).replace('%%ORDER%%', json.dumps(['inicio'] + flat))
open(OUT_PATH, 'w', encoding='utf-8').write(out)
print('ok', len(out), 'bytes;', len(flat), 'pages')
