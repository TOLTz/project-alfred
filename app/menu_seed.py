import json
from app.db import SessionLocal, MenuItem

DEFAULT_MENU = [
    {
        "item_id": "QUEIJO_QUENTE",
        "name": "Queijo quente",
        "aliases": ["pao com queijo", "pão com queijo", "queixo quente", "queijo quenti", "pão com quero"],
    },
    {
        "item_id": "COCA_ZERO_LATA",
        "name": "Coca-Cola Zero (lata)",
        "aliases": ["coca zero", "coca cola zero", "coca 0", "coca zero lata"],
    },
    {
        "item_id": "COXINHA_FRANGO",
        "name": "Coxinha de Frango",
        "aliases": ["coxinha", "coxina", "coxinha de frango com catupiry", "salgado de frango"],
    },
    {
        "item_id": "PAO_DE_QUEIJO_UN",
        "name": "Pão de Queijo",
        "aliases": ["pao de queijo", "pãozinho de queijo", "pao de keijo", "pdq"],
    },
    {
        "item_id": "SUCO_LARANJA_500",
        "name": "Suco de Laranja (500ml)",
        "aliases": ["suco de laranja", "suco natural", "laranja natural", "suco de laranxa"],
    },
    {
        "item_id": "HAMBURGUER_ARTESANAL",
        "name": "Hambúrguer Artesanal",
        "aliases": ["burguer", "hamburgue", "X-burguer", "cheeseburguer", "lanche"],
    },
    {
        "item_id": "BATATA_FRITA_M",
        "name": "Batata Frita (Média)",
        "aliases": ["batata", "fritas", "porção de batata", "batata frita media"],
    },
    {
        "item_id": "MISTO_QUENTE",
        "name": "Misto Quente",
        "aliases": ["misto", "pão com presunto e queijo", "misto quente caprichado"],
    },
    {
        "item_id": "ESFIHA_CARNE",
        "name": "Esfiha de Carne",
        "aliases": ["esfiha", "esfirra", "esfirra de carne", "salgado de carne"],
    },
    {
        "item_id": "CAFE_EXPRESSO",
        "name": "Café Expresso",
        "aliases": ["cafe", "cafézinho", "expresso", "cafezinho", "café preto"],
    },
    {
        "item_id": "AGUA_MINERAL_S_GAS",
        "name": "Água Mineral Sem Gás",
        "aliases": ["agua", "água", "agua sem gas", "garrafa de agua"],
    },
    {
        "item_id": "AGUA_MINERAL_C_GAS",
        "name": "Água Mineral Com Gás",
        "aliases": ["agua com gas", "água com gás", "agua gaseificada"],
    },
    {
        "item_id": "BOLO_CENOURA_FATIA",
        "name": "Bolo de Cenoura (fatia)",
        "aliases": ["bolo de cenoura", "bolo com cobertura de chocolate", "fatia de bolo"],
    },
    {
        "item_id": "CERVEJA_LATA",
        "name": "Cerveja (lata)",
        "aliases": ["cerveja", "breja", "gelada", "latinha"],
    },
    {
        "item_id": "BRIGADEIRO_UN",
        "name": "Brigadeiro Gourmet",
        "aliases": ["doce", "brigadeiro", "neguinho", "docinho"],
    },
    {
        "item_id": "ACAI_TIGELA_500",
        "name": "Açaí na Tigela (500ml)",
        "aliases": ["acai", "açaí", "assai", "tigela de açaí"],
    },
    {
        "item_id": "SANDUICHE_NATURAL",
        "name": "Sanduíche Natural de Frango",
        "aliases": ["sanduiche leve", "lanche natural", "sanduiche de frango"],
    },
    {
        "item_id": "CAPUCCINO_G",
        "name": "Capuccino Grande",
        "aliases": ["capuccino", "capuchino", "café com leite e chocolate"],
    },
    {
        "item_id": "PAO_NA_CHAPA",
        "name": "Pão na Chapa",
        "aliases": ["pao com manteiga", "pão na chapa", "paozinho na chapa"],
    },
    {
        "item_id": "SUCO_DETOX",
        "name": "Suco Detox (Verde)",
        "aliases": ["suco verde", "detox", "suco de couve"],
    },
    {
        "item_id": "TORTA_FRANGO_FATIA",
        "name": "Torta de Frango",
        "aliases": ["fatia de torta", "torta salgada", "torta de frango"],
    },
    {
        "item_id": "CROISSANT_MANTEIGA",
        "name": "Croissant de Manteiga",
        "aliases": ["croassant", "croisat", "pão folhado"],
    },
]


def ensure_menu_seeded() -> None:
    db = SessionLocal()
    try:
        exists = db.query(MenuItem).first()
        if exists:
            return

        for it in DEFAULT_MENU:
            db.add(
                MenuItem(
                    item_id=it["item_id"],
                    name=it["name"],
                    aliases_json=json.dumps(it["aliases"], ensure_ascii=False),
                )
            )
        db.commit()
    finally:
        db.close()
