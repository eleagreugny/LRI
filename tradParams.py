# -*- coding: utf-8 -*-

from libsbgnpy.libsbgnTypes import GlyphClass, ArcClass

class ParamsLogToAF :
    """Paramètres utilisés dans TraductionAF."""

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

class ParamsAFtoLog:
    """Paramètres utilisés dans TraductionAFLog."""

    # dictionnaire de traduction des glyphs
    DIC_GLYPH = {GlyphClass.BIOLOGICAL_ACTIVITY : 'ba(',
    GlyphClass.PERTURBATION : 'perturbation(',
    GlyphClass.PHENOTYPE : 'phenotype(', GlyphClass.AND : 'and(',
    GlyphClass.OR : 'or(', GlyphClass.NOT: 'not(',
    GlyphClass.DELAY : 'delay(',
    GlyphClass.COMPARTMENT : 'compartment('}

    #dictionnaire de traduction des arcs
    DIC_ARC = {ArcClass.LOGIC_ARC : "input(",
    ArcClass.POSITIVE_INFLUENCE : "stimulates(",
    ArcClass.NEGATIVE_INFLUENCE : "inhibits(",
    ArcClass.UNKNOWN_INFLUENCE : "unknownInfluences(",
    ArcClass.NECESSARY_STIMULATION : "necessarilyStimulates("}

    #liste des operateurs logiques
    LOP = [GlyphClass.AND, GlyphClass.OR, GlyphClass.NOT,
    GlyphClass.DELAY]

    #dictionnaire de correspondance pour les units of information
    DIC_UI = {'unspecified entity' : 'u',
    'simple chemical' : 'sc', 'macromolecule' : 'm',
    'nucleic acid feature' : 'naf', 'complex' : 'c',
    'perturbation' : 'p'}

class TraductionError(Exception):
    
    def __init__(self, msg):
        super(TraductionError, self).__init__(msg)

class DuplicateError(TraductionError):
    
    def __init__(self, msg):
        super(DuplicateError, self).__init__(msg)

class MissingGlyphError(TraductionError):

    def __init__(self, msg):
        super(MissingGlyphError, self).__init__(msg)

class GlyphClassError(TraductionError):

    def __init__(self, msg):
        super(GlyphClassError, self).__init__(msg)
