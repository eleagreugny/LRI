# -*- coding: utf-8 -*-

from libsbgnpy.libsbgnTypes import GlyphClass, ArcClass

class ParamsLogToAF :

    #résolution de l'image : pixels / inch 
    RESOLUTION = 120

    #hauteur de la box d'une unité d'information d'un compartment
    HEIGHT_COMPARTMENT_UOI = 20

    #hauteur de la box d'une unité d'information des autres glyphs
    HEIGHT_GLYPH_UOI = 16

    #largeur d'une bbox d'uoi vide
    WIDTH_EMPTY_UOI = 15

    #largeur max d'une lettre (w)
    WIDTH_MAX_LETTER = 10

    #dimension de la box d'un opérateur logique
    LOG_OP_DIM = 42

    #dictionnaire des types de glyphes
    DIC_GLYPH_TYPE = {'ba' : GlyphClass.BIOLOGICAL_ACTIVITY,
    'perturbation' : GlyphClass.PERTURBATION,
    'phenotype' : GlyphClass.PHENOTYPE, 'and' : GlyphClass.AND,
    'or' : GlyphClass.OR, 'not' : GlyphClass.NOT,
    'delay' : GlyphClass.DELAY, 'compartment' : GlyphClass.COMPARTMENT,
    'biologicalActivity' : GlyphClass.BIOLOGICAL_ACTIVITY}

    #dictionnaire de type d'arcs
    DIC_ARC_TYPE = {'input' : ArcClass.LOGIC_ARC,
    'stimulates' : ArcClass.POSITIVE_INFLUENCE,
    'inhibits' : ArcClass.NEGATIVE_INFLUENCE,
    'unknownInfluences' : ArcClass.UNKNOWN_INFLUENCE,
    'necessarilyStimulates' : ArcClass.NECESSARY_STIMULATION}

    #dictionnaire de type d'unité d'information
    DIC_UI_TYPE = {'macromolecule' : 'macromolecule',
    'naf' : 'nucleic acid feature', 'complex' : 'complex',
    'simplechemical' : 'simple chemical',
    'unspecifiedentity' : 'unspecified entity', 'void' : '"void"'}

    #dictionnaire des opérateurs logiques et labels associés
    DIC_LOG_OP = {GlyphClass.AND : 'AND', GlyphClass.OR : 'OR',
    GlyphClass.NOT : 'NOT', GlyphClass.DELAY : 'T'}

