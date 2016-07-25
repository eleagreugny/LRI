#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import libsbgnpy.libsbgn as libsbgn  # import the bindings
from libsbgnpy.libsbgnUtils import print_bbox # some additional helpers
from libsbgnpy.libsbgnTypes import Language, GlyphClass, ArcClass

class TraductionAFLog:
	"""
	Cette classe permet de traduire un graphe SBGN-AF stocké
	sous forme SBGN-ML dans un fichier .sbgn dans le langage 
	SBGN_AFLog sous forme de prédicats logiques.
	-----------------------------------------------------------
	@author: Elea Greugny
	@date: 06/07/2016
	"""

	def __init__(self, fichier):
		self.sbgn = libsbgn.parse(fichier)
		self.map = self.sbgn.get_map()
		self.glyphs = self.map.get_glyph()
		self.arcs = self.map.get_arc()
		#fichier texte qui contiendra la traduction en predicats
		self.tradlog = open("tradLog.txt", 'w')

		# dictionnaire de traduction des glyphs
		self.dic_glyph = {GlyphClass.BIOLOGICAL_ACTIVITY : 'ba(',
		GlyphClass.PERTURBATION : 'perturbation(',
		GlyphClass.PHENOTYPE : 'phenotype(', GlyphClass.AND : 'and(',
		GlyphClass.OR : 'or(', GlyphClass.NOT: 'not(',
		GlyphClass.DELAY : 'delay(',
		GlyphClass.COMPARTMENT : 'compartment('}
		#dictionnaire de traduction des arcs
		self.dic_arc = {ArcClass.LOGIC_ARC : "input(",
		ArcClass.POSITIVE_INFLUENCE : "stimulates(",
		ArcClass.NEGATIVE_INFLUENCE : "inhibits(",
		ArcClass.UNKNOWN_INFLUENCE : "unknownInfluences(",
		ArcClass.NECESSARY_STIMULATION : "necessarilyStimulates("}

		#compteur des operateurs logiques
		self.nb_op = 0
		#liste des operateurs logiques
		self.lop = [GlyphClass.AND, GlyphClass.OR, GlyphClass.NOT,
		GlyphClass.DELAY]

		#dictionnaire des nouveaux id des glyphs
		#(les anciens  id constituent les cles)
		self.dic_id = {}
		for g in self.glyphs:
			if g.get_id() in self.dic_id.keys() :
				print("Attention : plusieurs glyphs ont le même id.\n")
			else :
				self.dic_id[g.get_id()] = ''

		#dictionnaire de correspondance pour les units of information
		self.dic_ui = {'unspecified entity' : 'u',
		'simple chemical' : 'sc', 'macromolecule' : 'm',
		'nucleic acid feature' : 'naf', 'complex' : 'c',
		'perturbation' : 'p'}

		#compteur activites sans label
		self.nb_asl = 0

		#compteur de compartiments
		self.nb_comp = 0


	def glyphs_trad(self):
		"""glyphs_trad traduit chaque glyph du graphe en predicats
		en fonction du type du glyph. traduit aussi les label,
		unites auxiliaires et localisation."""
		for g in self.glyphs:
			cls = g.get_class()

			#traduction des glyphs en predicats
			if cls in self.dic_glyph.keys():
				self.tradlog.write(self.dic_glyph[cls]
				+self.dic_id[g.get_id()]+")\n")

			#traduction des localisations
			if g.get_compartmentRef():
				self.tradlog.write('localized('
				+ self.dic_id[g.get_id()] + ','
				+ self.dic_id[g.get_compartmentRef()] + ')\n')

			if cls not in self.lop:
				#traduction des labels en predicats
				try:
					label = g.get_label().get_text()
				except:
					label = ""
				self.tradlog.write('label('+self.dic_id[g.get_id()]
				+',"'+label+'")\n')

				#traduction des unites auxiliaires en predicats
				if g.get_glyph():
					if cls != GlyphClass.COMPARTMENT:
						ui = g.get_glyph()[0]
						try:
							ui_lab = ui.get_label().get_text()
						except:
							ui_lab = ""
						entity = ui.get_entity().get_name()
						if entity == 'nucleic acid feature':
							entity = 'naf'
						else:
							entity = entity.replace(" ", "")
						self.tradlog.write('uoi(' + self.dic_id[g.get_id()]
						+ ',' + entity + ',"' + ui_lab + '")\n')
					else:
						ui = g.get_glyph()[0]
						try:
							ui_lab = ui.get_label().get_text()
							if ':' in ui_lab:
								ui_lab = ui_lab.split(":")
								pre = ui_lab[0]
								lab = ui_lab[1]
							else:
								pre = 'void'
								lab = ui_lab
						except:
							pre = 'void'
							lab = ""
						self.tradlog.write('uoi(' + self.dic_id[g.get_id()]
						+ ',"' + pre + '","' + lab + '")\n')

	def arcs_trad(self):
		"""arcs_trad traduit chaque arc du graphe en predicats
		en fonction du type d'arc"""
		for a in self.arcs:
			cls = a.get_class()
			if cls in self.dic_arc.keys():
				source = a.get_source()
				target = a.get_target()
				if '.' in source:
					pos_s = source.find('.')
					source = source[:pos_s]
				if '.' in target:
					pos_t = target.find('.')
					target = target[:pos_t]
				self.tradlog.write(self.dic_arc[cls]+self.dic_id[source]
				+","+self.dic_id[target]+")\n")


	def rename_op(self, g):
		"""Associe le nouveau nom : o_self.nb_op au glyphe g de type
		operateur logique dans le dictionnaire self.dic_id"""
		self.nb_op += 1
		self.dic_id[g.get_id()] = 'o' + str(self.nb_op)

	def rename_ba(self, g):
		"""Associe un nouveau nom au glyphe g de type activite biologique,
		phenotype ou perturbation, dans le dictionniare self.dic_id.
		Le nouveau nom est construit de la facon suivante :
		label_aux_typeaux_comp
		label designe le label du glyphe g,
		aux le label de l'unite auxiliaire,
		typeaux le type de l'unite auxiliaire (voir self.dic_ui),
		comp le compartiment dans lequel se trouve le glyphe
		si il y a plusieurs compartiments dans le graphe
		et qu'il existe un même glyph dans un autre compartiment"""
		try:
			label = (g.get_label().get_text()).lower().replace(" ", "_")
		except:
			self.nb_asl += 1
			label = 'a'+str(self.nb_asl)

		if g.get_glyph():
			ui = g.get_glyph()[0]
			try:
				aux = (ui.get_label().get_text()).lower()
			except:
				aux = 'void'
			typeaux = self.dic_ui[ui.get_entity().get_name()]
			name = label + '_' + aux + '_' + typeaux
		else:
			name = label
			
		if g.get_compartmentRef() and self.nb_comp > 1:
			for g2 in self.glyphs:
				if g.get_id() != g2.get_id():
					if self.are_equal(g,g2):
						comp = self.dic_id[g.get_compartmentRef()]
						name = name + '_' + comp

		self.dic_id[g.get_id()] = name 

	def rename_comp(self, g):
		"""Associe une constante au glyphe g de type compartment"""
		name = g.get_glyph()[0].get_label().get_text().lower().replace(" ", "_")
		self.dic_id[g.get_id()] = name 

	def rename_glyph(self):
		"""Appelle les differentes methodes rename associees 
		aux differents types de glyphes"""
		for g in self.glyphs:
			cls = g.get_class()
			if cls in self.lop :
				self.rename_op(g)
			else :
				if cls != GlyphClass.COMPARTMENT :
					self.rename_ba(g)
				else :
					self.nb_comp += 1
					self.rename_comp(g)
		
	def are_equal(self, g1, g2):
		"""Teste si les glyphs g1 et g2 diffèrent seulement par
		les compartiments auxquels ils appartiennent.
		Renvoie true si c'est le cas."""
		cls1 = g1.get_class()
		cls2 = g2.get_class()
		if cls1 != cls2:
			#les glyphs ne sont pas de la même classe
			return False
		else:
			if (not g1.get_label() and g2.get_label()) or (g1.get_label() and not g2.get_label()):
				#un des glyphs n'a pas de label
				return False
			else:
				if g1.get_label() and g2.get_label():
					lab1 = g1.get_label().get_text()
					lab2 = g2.get_label().get_text()
					if lab1 != lab2:
					#les glyphs n'ont pas le même label
						return False
				#si les deux n'ont pas de label, on continue
				if (not g1.get_glyph()) and (not g2.get_glyph()):
					#les glyphs ne possèdent pas d'unité d'information
					#ils sont donc identiques
					comp1 = g1.get_compartmentRef()
					comp2 = g2.get_compartmentRef()
					if comp1 == comp2:
						print("Attention : deux glyphes identiques " +
						"dans le même compartiment.\n")
						return False
					else:
						#les glyphes ne diffèrent que par le compartiment
						return True
				else:
					if (not g1.get_glyph() and g2.get_glyph()) or (g1.get_glyph() and not g2.get_glyph()):
						#un des glyph n'a pas d'unité d'information
						return False
					else:
						ui1 = g1.get_glyph()[0]
						ui2 = g2.get_glyph()[0]
						ui1_cls = ui1.get_entity().get_name()
						ui2_cls = ui2.get_entity().get_name()
						if ui1_cls != ui2_cls:
							#les ui ne sont pas du même type
							return False
						else:
							if (not ui1.get_label() and ui2.get_label()) or (ui1.get_label() and not ui2.get_label()):
								return False
							else:
								if ui1.get_label() and ui2.get_label():
									ui1_lab = ui1.get_label().get_text()
									ui2_lab = ui2.get_label().get_text()
									if ui1_lab != ui2_lab:
										#les ui n'ont pas le même label
										return False
								#si les deux non pas de labels on continue
								comp1 = g1.get_compartmentRef()
								comp2 = g2.get_compartmentRef()
								if comp1 == comp2:
									print("Attention : deux glyphes " +
									"identiques " + "dans le même " +
									"compartiment.\n")
								else:
									return True
	
	def traduire(self):
		"""Enchainement des methodes pour obtenir la traduction 
		complète dans le fichier tradLog.txt"""
		self.rename_glyph()
		self.glyphs_trad()
		self.arcs_trad()
		self.tradlog.close()



#tests

test = TraductionAFLog('essai.sbgn')
test.traduire()
