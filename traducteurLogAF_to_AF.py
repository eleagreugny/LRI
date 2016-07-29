#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#from __future__ import print_function
#from __future__ import unicode_literals
import argparse
import codecs
from graphviz import Digraph
import re
import sys

import libsbgnpy.libsbgn as libsbgn  # import the bindings
from libsbgnpy.libsbgnTypes import Language, GlyphClass, ArcClass
from tradParams import *

class TraductionAF:
    """
    Cette classe permet de traduire un graphe SBGNLog-AF stocké dans un
    fichier texte en langage SBGN-AF avec la library libsbgnpy.
    Pour obtenir les positions absolues des arcs et des noeuds,
    on utilise la library graphviz (langage DOT).
    -------------------------------------------------------------------
    @author: Elea Greugny
    @date: 21/07/16
    """
    def __init__(self, fichier_entree, fichier_sortie):
        self.data = codecs.open(fichier_entree, 'r', 'utf8')
        self.sbgn = libsbgn.sbgn()
        self.map = libsbgn.map()
        self.map.set_language(Language.AF)
        self.sbgn.set_map(self.map)
        self.f_out = fichier_sortie
        #résolution de l'image : pixels / inch
        self.resolution = ParamsLogToAF.RESOLUTION

        #compteur de glyphs
        self.nb_glyph = 0
        #compteur d'arcs
        self.nb_arc = 0

        #dictionnaire qui fait correspondre les constantes logiques
        #associées aux glyphes (clé) avec les glyphs eux-mêmes.
        self.dic_const_glyph = {}

        #dictionnaire qui relie les glyphs (clés) aux arcs auxquels ils
        #participent en tant que source ou target, stockés sous forme
        #de liste de tuples : ('s' ou 't', arc).
        self.dic_glyph_arc = {}

        #dictionnaire qui permet d'accéder aux glyphs à partir de leur
        #id (clé)
        self.dic_id_glyph = {}

        #dictionnaire qui permet d'accéder aux glyphs contenus dans
        #un compartment (clé)
        self.dic_comp = {}

        #liste des glyphs n'appartenant à aucun compartment
        #initialisée quand tous les glyphs sont créés
        self.single_glyph = []

        #dictionnaire de fonctions:
        #associe un predicat à la fonction correpondante.
        self.dic_func = {'compartment' : self.create_glyph,
        'ba' : self.create_glyph, 'perturbation' : self.create_glyph,
        'phenotype' : self.create_glyph, 'and' : self.create_glyph,
        'or' : self.create_glyph, 'not' : self.create_glyph,
        'delay' : self.create_glyph, 'label' : self.create_label,
        'input' : self.create_arc, 'stimulates' : self.create_arc,
        'inhibits' : self.create_arc,
        'unknownInfluences' : self.create_arc,
        'necessarilyStimulates' : self.create_arc,
        'localized' : self.create_localisation,
        'uoi' : self.create_unitOfInformation,
        'biologicalActivity' : self.create_glyph}

        #Graphe en langage DOT
        self.dot_graph = Digraph('G', filename='position_graph_sbgn.gv',
        format='plain', encoding='utf8')

        #hauteur et largeur du graphe en pixels : mise à jour au moment
        #de la lecture du fichier .gv.plain
        self.max_height = 0
        self.max_width = 0

    def create_glyph(self, const, cls):
        """Crée un objet glyph de type cls.
        L'id sera 'glyphN' où N est le numero du glyph, incrémenté
        à chaque création de glyph."""
        self.nb_glyph += 1
        box = libsbgn.bbox()
        gly = libsbgn.glyph(class_=cls, id='glyph' +
        str(self.nb_glyph), bbox=box)
        self.map.add_glyph(gly)
        if const in self.dic_const_glyph.keys():
            text = """The same logical constant '""" + const + """' may be
            associated with several glyphs or the glyph '""" + const + """'
            may be declared several times."""
            raise DuplicateError(text)
        else:
            self.dic_const_glyph[const] = gly
            self.dic_glyph_arc[gly] = []
            self.dic_id_glyph[gly.get_id()] = gly
            if cls == GlyphClass.COMPARTMENT:
                self.dic_comp[gly] = []

    def create_arc(self, const_s, const_t, cls_arc):
        """Crée un objet arc de type cls_a.
        const_s et const_t désignent les constantes logiques associées
        aux glyphes source et target respectivement. Ces glyphs doivent
        être présents dans self.dic_const_glyph.
        L'id sera arcN où N est le numéro de l'arc, incrémenté
        à chaque création d'arc."""
        self.nb_arc += 1
        try:
            sour = self.port_management(self.dic_const_glyph[const_s])
        except KeyError:
            msg = """The source glyph '""" + const_s + """' used in this
            arc has not been declared."""
            raise MissingGlyphError(msg)
        try:
            targ = self.port_management(self.dic_const_glyph[const_t])
        except KeyError:
            msg = """The target glyph '""" + const_t + """' used in this
            arc has not been declared."""
            raise MissingGlyphError(msg)
        arc = libsbgn.arc(class_=cls_arc, source=sour, target=targ,
        id='arc' + str(self.nb_arc))
        self.map.add_arc(arc)
        self.dic_glyph_arc[self.dic_const_glyph[const_s]].append(('s', arc))
        self.dic_glyph_arc[self.dic_const_glyph[const_t]].append(('t', arc))

    def port_management(self, gly):
        """Cette méthode permet de gérer les ports d'un glyph au moment
        de l'ajout d'un arc. Si le glyph participe déjà à plusieurs arcs
        (autrement dit, il a déjà des ports), on crée un nouveau port.
        Si le glyph n'est lié qu'à un seul arc (il n'a pas de port),
        on crée deux ports, un premier sur lequel va se lier l'arc déjà
        présent, et un autre pour le nouvel arc. Si le glyph n'est lié
        à aucun arc, le nouvel arc se lie directement au glyph, pas
        besoin de port. Dans tous les cas, la méthode renvoie l'id de
        l'objet sur lequel va s'attacher le nouvel arc."""
        if len(self.dic_glyph_arc[gly]) == 0:
            return gly.get_id()
        else:
            port_id = (gly.get_id() + '.' +
            str(len(self.dic_glyph_arc[gly])+1))
            port = libsbgn.port(id=port_id)
            gly.add_port(port)
            if len(self.dic_glyph_arc[gly]) == 1:
                port_id2 = (gly.get_id() + '.' +
                str(len(self.dic_glyph_arc[gly])))
                port2 = libsbgn.port(id=port_id2)
                gly.add_port(port2)
                first_arc_tuple = self.dic_glyph_arc[gly][0]
                if first_arc_tuple[0] == 's':
                    first_arc_tuple[1].set_source(port2.get_id())
                else:
                    first_arc_tuple[1].set_target(port2.get_id())
            return port.get_id()

    def create_label(self, const_g, lab):
        """Crée un objet label avec  pour attribut text la chaîne
        de caractère lab passée en paramètre, et l'associe au glyphe
        de constante logique const grâce au dictionnaire d'id."""
        lab = lab.encode('utf8')
        lab = lab.replace('"', '')
        label = libsbgn.label(text=lab.decode('utf8'))
        try:
            self.dic_const_glyph[const_g].set_label(label)
        except KeyError:
            msg = """The glyph '""" + const_g + """' has not been
            declared."""
            raise MissingGlyphError(msg)

    def create_localisation(self, const_g, const_c):
        """Affecte le glyphe de constante logique const_g
        au compartiment de constante logique const_c"""
        try:
            gly = self.dic_const_glyph[const_g]
        except KeyError:
            msg = """The glyph '""" + const_g + """' has not been
            declared."""
            raise MissingGlyphError(msg)
        try:
            comp = self.dic_const_glyph[const_c]
        except KeyError:
            msg = """The compartment '""" + const_c + """' has not been
            declared."""
            raise MissingGlyphError(msg)
        gly.set_compartmentRef(comp.get_id())
        self.dic_comp[comp].append(gly)
        del self.single_glyph[self.single_glyph.index(gly)]

    def create_unitOfInformation(self, const_g, cls_ui, label_ui):
        """Affecte un glyphe de type unit of information au glyphe
        de constante logique const_g. La classe de l'unité d'information
        est donnée par cls_ui. Son label, qui peut être vide est donné
        en paramètre. Cette méthode crée donc deux objets : le label
        de l'unité d'information et le glyph de type unité d'information.
        L'id de l'unité d'information est constitué de celui du glyphe
        auquel elle appartient, auquel on ajoute une lettre."""
        box = libsbgn.bbox()
        try:
            uoi = libsbgn.glyph(class_=GlyphClass.UNIT_OF_INFORMATION,
            id=str(self.dic_const_glyph[const_g].get_id())+'a', bbox=box)
        except KeyError:
            msg = """The glyph '""" + const_g + """' has not been
            declared."""
            raise MissingGlyphError(msg)
        if self.dic_const_glyph[const_g].get_class() != GlyphClass.COMPARTMENT:
            lab = label_ui.encode('utf8')
            lab = label_ui.replace('"', '')
            lab = libsbgn.label(text=lab)#.decode('utf8'))
            uoi.set_label(lab)

            ent = libsbgn.entityType(name=cls_ui)
            uoi.set_entity(ent)
        else:
            cls_ui = cls_ui.replace('"', '')
            label_ui = label_ui.replace('"', '')
            if cls_ui == 'void':
                lab = libsbgn.label(text=label_ui)
            else:
                lab = libsbgn.label(text=cls_ui + ':' + label_ui)
            uoi.set_label(lab)

        self.dic_const_glyph[const_g].add_glyph(uoi)

    def logic_nodes_localisation(self):
        """Place les glyphs logiques (or, and, not, delay) dans le
        compartment d'un de leur input. Si aucun de leur input n'est
        associé à un compartment, le glyph reste sans compartment."""
        for gly in self.single_glyph:
            if gly.get_class() in ParamsLogToAF.DIC_LOG_OP.keys():
                for couple in self.dic_glyph_arc[gly]:
                    if couple[0] == 't':
                        id_source = couple[1].get_source()
                        if '.' in id_source:
                            id_source = id_source[:id_source.find('.')]
                        source = self.dic_id_glyph[id_source]
                        if source.get_compartmentRef():
                            comp = self.dic_id_glyph[
                            source.get_compartmentRef()]
                            self.dic_comp[comp].append(gly)
                            del self.single_glyph[
                            self.single_glyph.index(gly)]
                            break

    def LogAF_to_AF(self):
        """Lis le fichier d'entrée dans le langage SBGN-AF
        et crée les objets correspondants dans la library libsbgnpy."""
        data = self.data.readlines()
        for line in data:
            #premier parcours pour créer tous les glyphs
            line = re.split('[(,)]', line)
            predicate = line[0]
            if len(line) == 3:
                #predicats du type : predicat(a)
                const = line[1]
                try:
                    cls = ParamsLogToAF.DIC_GLYPH_TYPE[predicate]
                except KeyError:
                    msg = """'""" + predicate + """' doesn't match
                    any glyph type. The allowed types are : ba/biologicalActivity,
                    perturbation, phenotype, and, or, not, delay,
                    compartment."""
                    raise GlyphClassError(msg)
                params = [const, cls]
                func = self.dic_func[predicate]
                func(*params)
            self.single_glyph = list(self.map.get_glyph())

        for line in data:
            #second parcours pour les autres prédicats
            split_line = re.split('[(,)]', line)
            predicate = split_line[0]
            if predicate in ParamsLogToAF.DIC_ARC_TYPE.keys():
                const_s = split_line[1]
                const_t = split_line[2]
                cls_a = ParamsLogToAF.DIC_ARC_TYPE[predicate]
                params = [const_s, const_t, cls_a]
                func = self.dic_func[predicate]
                func(*params)
            else:
                if len(split_line) == 4:
                    #predicats du type : predicat(a,b)
                    if predicate in self.dic_func.keys():
                        const = split_line[1]
                        arg = split_line[2]
                        params = [const, arg]
                        func = self.dic_func[predicate]
                        func(*params)
                    else:
                        msg = """This line doesn't seem
                        to match any logical predicate.\n""" + line
                        raise PredicateError(msg)
                elif len(split_line) == 5:
                    #predicats du type : predicat(a,b,c)
                    #(affectation des unités auxiliaires)
                    if predicate in self.dic_func.keys():
                        const_g = split_line[1]
                        cls_ui = ParamsLogToAF.DIC_UI_TYPE[
                        split_line[2].replace('"', '')]
                        label = split_line[3]
                        params = [const_g, cls_ui, label]
                        func = self.dic_func[predicate]
                        func(*params)
                    else:
                        msg = """This line doesn't seem
                        to match any logical predicate.\n""" + line
                        raise PredicateError(msg)
                elif len(split_line) != 0 and (split_line[0] not in
                ParamsLogToAF.DIC_GLYPH_TYPE.keys()):
                    msg = """This line doesn't seem
                    to match any logical predicate.\n""" + line
                    raise PredicateError(msg)

        self.logic_nodes_localisation()
        self.create_dot_graph()
        self.dot_graph.render('position_graph.gv', view=False)
        self.read_dot()

    def create_dot_graph(self):
        """Cette méthode permet d'implémenter le graph SBGN en
        langage DOT. On ne cherche pas à reproduire la mise en forme
        particulière des graphs SBGN car on s'intéresse seulement aux
        positions absolues des noeuds et des arcs."""
        #création des node inclus dans des compartments (clusters)
        comp_index = 0
        for comp in self.dic_comp.keys():
            cluster_name = 'cluster_' + str(comp_index)
            c = Digraph(cluster_name, encoding='utf8')
            for glyph in self.dic_comp[comp]:
                if glyph.get_class() in ParamsLogToAF.DIC_LOG_OP.keys():
                    c.node(glyph.get_id(),
                    label=ParamsLogToAF.DIC_LOG_OP[glyph.get_class()],
                    shape='circle')
                else:
                    if glyph.get_label():
                        c.node(glyph.get_id(),
                        label=glyph.get_label().get_text().decode('utf8'))
                    else:
                        c.node(glyph.get_id())
            self.dot_graph.subgraph(c)
            comp_index += 1
        #création des node hors compartment
        for glyph in self.single_glyph:
            if glyph.get_class() in ParamsLogToAF.DIC_LOG_OP.keys():
                self.dot_graph.node(glyph.get_id(),
                label=ParamsLogToAF.DIC_LOG_OP[glyph.get_class()],
                shape='circle')
            else:
                if glyph.get_label():
                    self.dot_graph.node(glyph.get_id(),
                    label=glyph.get_label().get_text())
                else:
                    self.dot_graph.node(glyph.get_id())
        #création des arcs
        for arc in self.map.get_arc():
            if '.' in arc.get_source():
                source = arc.get_source()[:arc.get_source().find('.')]
            else:
                source = arc.get_source()
            if '.' in arc.get_target():
                target = arc.get_target()[:arc.get_target().find('.')]
            else:
                target = arc.get_target()
            self.dot_graph.edge(source, target, tailclip='true')

    def coord_dot_to_sbgn(self, xdot, ydot):
        """En langage DOT, les coordonnées sont données en inch tandis
        qu'en SBGN elles le sont en pixels.
        L'origine d'un graphe DOT est située dans le coin en bas à
        gauche tandis que celle d'un graphe SBGN est située dans le
        coin supérieur gauche. Cette méthode permet donc de convertir
        les coordonnées DOT en coordonnées SBGN. Elle renvoie un tuple
        (xsbgn, ysbgn)."""
        xsbgn = xdot * self.resolution + 0.025 * self.max_width
        ysbgn = 1.025 * self.max_height - ydot * self.resolution
        return (xsbgn, ysbgn)

    def change_origin_glyph(self, xdot, ydot, wdot, hdot):
        """En langage DOT, les coordonnées sont données en inch tandis
        qu'en SBGN elles le sont en pixels.
        L'origine d'un graphe DOT est située dans le coin en bas à
        gauche tandis que celle d'un graphe SBGN est située dans le
        coin supérieur gauche.
        De plus, en langage DOT, un glyph est caractérisé par le centre
        du rectangle, tandis que le langage SBGN le caractérise
        par son soin supérieur gauche. Cette méthode permet donc de
        calculer les coordonnées du coin supérieur gauche d'un glyph,
        à partir de celles du centre de son rectangle exprimées en inch.
        Cette méthode renvoie un tuple (xsbgn, ysbgn, wsbgn, hsbgn)"""
        wsbgn = wdot * self.resolution
        hsbgn = hdot * self.resolution
        xsbgn = xdot * self.resolution - (wsbgn/2.0) + self.max_width * 0.025
        ysbgn = 1.025 * self.max_height - ydot * self.resolution - (hsbgn/2.0)
        return (xsbgn, ysbgn, wsbgn, hsbgn)

    def change_origin_logop(self, xdot, ydot):
        """En langage DOT, les coordonnées sont données en inch tandis
        qu'en SBGN elles le sont en pixels.
        L'origine d'un graphe DOT est située dans le coin en bas à
        gauche tandis que celle d'un graphe SBGN est située dans le
        coin supérieur gauche.
        De plus, en langage DOT, un glyph est caractérisé par le centre
        du rectangle, tandis que le langage SBGN le caractérise
        par son soin supérieur gauche.
        Cette méthode permet donc de calculer les coordonnées du coin
        supérieur gauche d'un glyph de type opérateur logique
        de dimension ParamsLogToAF.LOG_OP_DIM, à partir de celles du centre
        de son rectangle exprimées en inch.
        Cette méthode renvoie un tuple (xsbgn, ysbgn)"""
        dsbgn = ParamsLogToAF.LOG_OP_DIM
        xsbgn = xdot * self.resolution - (dsbgn/2.0) + self.max_width * 0.025
        ysbgn = 1.025 * self.max_height - ydot * self.resolution - (dsbgn/2.0)
        return (xsbgn, ysbgn)

    def set_glyph_position(self, id_g, xdot, ydot, wdot, hdot):
        """Calcul des coordonnées x et y du glyph d'identifiant id_g
        à partir des cordonnées xdot et ydot fournies par DOT."""
        gly = self.dic_id_glyph[id_g]
        if gly.get_class() in ParamsLogToAF.DIC_LOG_OP.keys():
            (x_gly, y_gly) = self.change_origin_logop(xdot, ydot)
            w_gly = ParamsLogToAF.LOG_OP_DIM
            h_gly = ParamsLogToAF.LOG_OP_DIM
        else:
            (x_gly, y_gly, w_gly, h_gly) = self.change_origin_glyph(xdot,
            ydot, wdot, hdot)
        box = libsbgn.bbox(x=x_gly, y=y_gly, w=w_gly,
        h=h_gly)
        gly.set_bbox(box)
        if gly.get_glyph():
            self.set_uoi_position(gly)

    def set_comp_position(self, id_comp):
        """Calculs des coordonnées du compartment d'identifiant id_comp
        ainsi que la hauteur et la largeur de sa bbox à partir des bbox
        des glyphs qu'il contient."""
        comp = self.dic_id_glyph[id_comp]
        x_pot_min = [gly.get_bbox().get_x() for gly in self.dic_comp[comp]]
        y_pot_min = [gly.get_bbox().get_y() for gly in self.dic_comp[comp]]
        x_pot_max = [gly.get_bbox().get_x() + gly.get_bbox().get_w()
        for gly in self.dic_comp[comp]]
        y_pot_max = [gly.get_bbox().get_y() + gly.get_bbox().get_h()
        for gly in self.dic_comp[comp]]
        x_min = min(x_pot_min)
        x_max = max(x_pot_max)
        y_min = min(y_pot_min)
        y_max = max(y_pot_max)

        w_comp = (x_max - x_min) * 1.1
        h_comp = (y_max - y_min) * 1.1
        x_comp = x_min - 0.05 * w_comp
        y_comp = y_min - 0.05 * h_comp
        box = libsbgn.bbox(x=x_comp, y=y_comp, w=w_comp, h=h_comp)
        comp.set_bbox(box)
        if comp.get_glyph():
            self.set_uoi_position(comp)

    def set_uoi_position(self, gly):
        """Calcul des dimensions de la bbox de l'unité d'information du
        glyph gly. Les coordonnées de gly doivent avoir été calculées
        avant."""
        if gly.get_class() == GlyphClass.COMPARTMENT:
            h_uoi = ParamsLogToAF.HEIGHT_COMPARTMENT_UOI
        else:
            h_uoi = ParamsLogToAF.HEIGHT_GLYPH_UOI

        try:
            w_uoi = (ParamsLogToAF.WIDTH_EMPTY_UOI +
            ParamsLogToAF.WIDTH_MAX_LETTER *
            len(gly.get_glyph()[0].get_label().get_text()))
        except AttributeError:
            w_uoi = ParamsLogToAF.WIDTH_EMPTY_UOI

        x_gly = gly.get_bbox().get_x()
        y_gly = gly.get_bbox().get_y()
        w_gly = gly.get_bbox().get_w()

        x_uoi = x_gly + 0.1 * w_gly
        y_uoi = y_gly - h_uoi / 2.0

        box = libsbgn.bbox(x=x_uoi, y=y_uoi, w=w_uoi, h=h_uoi)
        gly.get_glyph()[0].set_bbox(box)

    def set_arc_position(self, id_source, id_target, points):
        """Calcul du tracé de l'arc reliant source à target, passant
        par les éléments de la liste points (tuples (x, y))"""
        source = self.dic_id_glyph[id_source]
        #recherche de l'arc
        for couple in self.dic_glyph_arc[source]:
            if couple[0] == 's':
                possible_target = couple[1].get_target()
                if '.' in possible_target:
                    possible_target = possible_target[
                    :possible_target.find('.')]
                if possible_target == id_target:
                    arc = couple[1]
                    break
        #mise en forme des points
        trace = []
        for p in points:
            x_p = p[0]
            y_p = p[1]
            (x_p, y_p) = self.coord_dot_to_sbgn(x_p, y_p)
            trace.append(libsbgn.point(x=x_p, y=y_p))
        #ajout des points à l'arc
        if len(trace) > 2:
            #arc.set_start(trace[0])
            arc.set_start(trace[1])
            #arc.set_next(trace[1:len(trace)-1])
        else:
            arc.set_start(trace[0])
        arc.set_end(trace[-1])
        #implémentation des coordonnées des éventuels ports
        if '.' in arc.get_source():
            self.set_port_position(arc.get_source(), id_source, trace[0])
        if '.' in arc.get_target():
            self.set_port_position(arc.get_target(), id_target, trace[-1])

    def set_port_position(self, id_port, id_glyph, point):
        """Implémentation des coordonnées x et y du port d'identifiant
        id_port appartenant au glyph d'identifiant id_glyph. L'objet point
        donné en paramètre correspond à l'extrémité d'un arc auquel
        participe le port. Si le port n'a pas encore de coordonnées, on
        prendra celles de ce point. Sinon, on conserve les précédentes."""
        gly = self.dic_id_glyph[id_glyph]
        for port in gly.get_port():
            if port.get_id() == id_port:
                if not port.get_x() and not port.get_y():
                    port.set_x(point.get_x())
                    port.set_y(point.get_y())
                break

    def read_dot(self):
        """Lecture du fichier .gv.plain et récupération des
        positions des glyphs et des arcs."""
        dot = codecs.open('position_graph.gv.plain', 'r', 'utf8')
        lines = dot.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].split()
        self.map.set_bbox(libsbgn.bbox(x=0, y=0,
        w=float(lines[0][2]) * self.resolution * 1.05,
        h=float(lines[0][3]) * self.resolution * 1.05))
        self.max_height = float(lines[0][3]) * self.resolution
        self.max_width = float(lines[0][2]) * self.resolution
        for line in lines[1:]:
            #premier passage pour les positions des glyphs
            #sauf ceux de type Compartment
            if line[0] == 'node':
                if self.dic_id_glyph[line[1]] not in self.dic_comp.keys():
                    self.set_glyph_position(line[1], float(line[2]),
                    float(line[3]), float(line[4]), float(line[5]))
            elif line[0] == 'edge':
                nb_points = int(line[3])
                points = []
                for i in range(0, 2 * nb_points, 2):
                    points.append((float(line[4 + i]), float(line[4 + i + 1])))
                self.set_arc_position(line[1], line[2], points)
        for line in lines[1:]:
            #deuxieme passage pour les positions des compartments
            if (line[0] == 'node' and
            (self.dic_id_glyph[line[1]] in self.dic_comp.keys())):
                self.set_comp_position(line[1])
        dot.close()

    def output_f(self):
        """Création du fichier de sortie .sbgn"""
        self.sbgn.write_file(self.f_out)

    def translation(self):
        """Enchainement des méthodes pour traduire le graphe SBGNLog-AF
        en graph SBGN-AF."""
        self.LogAF_to_AF()
        self.output_f()
    

