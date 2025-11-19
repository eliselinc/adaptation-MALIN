// var id_cahier : défini avant
//
function dbug(trucs) {
	if(typeof(console) == "object") {
		console.log(trucs);
	}
}
function stopPropa(event) {
	if(typeof(event) == "undefined") return;
	event.cancelBubble = true;
	if (event.stopPropagation) {
		event.stopPropagation();
	}
}
/*
	paramètres devant être définis plus haut
	même si initialisés plus bas
*/
/* système de pagination */
var page_courante = 1;
var total_pages = 1;
var montre_page;
var exo_en_cours = null;
/*
	système permettant aux exercices de s'enregitrer
	et traitements communs
*/
var print_exo_defaut = function(){};
var liste_exercices = new Array();
// appeler les prints de chaque exo
function tout_imprimer() {
	montre_page(total_pages);
	var sortie = new Array();
	$("#print").html("");
	$("#enonce").html("");
	// pour chaque exercice
	for(i=0; i<liste_exercices.length; i++) {
		if(liste_exercices[i].print) {
			// ajouter l'énoncé
			if($("."+liste_exercices[i].id_exo+" div.enonce").length) {
				var enonce = $("."+liste_exercices[i].id_exo+" div.enonce").html();
				enonce = $("<div class='subenonce " +liste_exercices[i].id_type +" " +liste_exercices[i].id_exo +"'></div>").append(enonce);
				enonce.find("br").remove();
				$("#print").append(enonce);
			}
			// préparer l'impression de l'exercice
			var conteneur = $('<div class="'+liste_exercices[i].id_exo+'" />');
			print_exo_defaut(liste_exercices[i].id_exo,conteneur);
			$("#print").append(conteneur);
			// trait de séparation
			$("#print").append('<br class="' +liste_exercices[i].id_type+'"/>');
		}
	}
	//
	$("#cahier_bouton_imprimer, #bottom, #cleft, #cright").hide();
	$("#toutes_pages").children().not(".pagefin").hide();

	$("#bloc_central").css({
		margin:"0px",
		height:"auto"
	});
	$(".pagefin").css({
		position:"relative",
		width:"auto",
		height:"auto"
	});
	$("#toutes_pages").css({
		width:"auto",
		height:"auto"
	});
	
	// TODO window.print();
}
//
/*
	système de "cookie"
*/
var storage_exos;
if(typeof(localStorage) == "object") {
	Storage.prototype.setObject = function(key, value) {
		this.setItem(key, JSON.stringify(value));
	};
	Storage.prototype.getObject = function(key) {
		return JSON.parse(this.getItem(key));
	};
	//
	storage_exos = JSON.parse(localStorage.getItem(id_cahier));
	if(storage_exos == null || storage_exos['type'] != "cahier") {
		storage_exos = new Object();
		storage_exos['type'] = "cahier";
	}
	storage_exos.save = function() {
		var dd = new Date();
		storage_exos['mdate'] = dd.toString();
		storage_exos['mtime'] = dd.getTime(); // ms
		localStorage.setObject(id_cahier,storage_exos);
	};
	// récupérer les réponses des exercices
	storage_exos.get = function(stid, defaut) {
		if(typeof(storage_exos[stid]) == "undefined") {
			return defaut;
		} else {
			return storage_exos[stid];
		}
	};
	// récupérer une valeur générique
	storage_exos.getGlobal = function(stid) {
		return localStorage.getItem(stid);
	}
	// enregistrer et restaurer les réponse d'exercices
	storage_exos.set = function(stid, vars) {
		storage_exos[stid] = vars;
	};
	storage_exos.unset = function(stid) {
		delete storage_exos[stid];
	};
	// remettre à 0 les réponses
	storage_exos.tout_reset = function() {
		delete(localStorage[id_cahier]);
		window.location.reload();
	};
} else {
	storage_exos = new Object();
	storage_exos['type'] = "cahier";
	storage_exos.save = function() {};
	storage_exos.get = function(stid, defaut) {};
	storage_exos.getGlobal = function(stid) {};
	storage_exos.set = function(stid, vars) {};
	storage_exos.unset = function(stid) {};
	storage_exos.tout_reset = function() {
		window.location.reload();
	};
	$(function(){ $("#oups").remove(); });
}
/*
	classes de types de variables
	s'utilise avec: data-mvt="blabla"
*/
var managed_var_types = {
	coche: {
		reset: function(that) {
			that.removeClass("sel0 sel1 sel2 sel3 sel4 sel5 sel6 sel7 sel8 sel9");
		}
	},
	input: {
		reset: function(that) {
			if(that.data("defaut")) {
				that.val(that.data("defaut"));
			} else {
				that.val("");
			}
		}
	},
	champ: {
		reset: function(that) {
			if(that.data("defaut")) {
				that.html(that.data("defaut"));
			} else {
				that.html("");
			}
			var content = that.html().replace(/<[^><]+>/g,"");
			var len = content.length;
			that.css({
				paddingLeft:Math.max(5,30-5*len)+"px",
				paddingRight:Math.max(5,30-5*len)+"px",
			});
		}
	},
	qcm: {
		reset: function(that) {
			that.html(that.data("defaut"));
		}
	},
	echange: {
		reset: function(that) {
			var stid = that.attr('id');
			var target = that.data('pos');
			if(target) {
				that.after('<span class="placeholder_echange '+stid+'" />');
				if($(".placeholder_echange."+target).length>0) {
					$(".placeholder_echange."+target).after(that);
				} else {
					$("#"+target).after(that);
				}
			}
			that.removeData('pos');
		}
	}
}
// remettre à 0 les réponses de la page courante
function reset_cette_page() {
	$("#loading").show();
	setTimeout(function() {
		$("#p"+page_courante+" .managed_var").each(function() {
			var type = $(this).data("mvt");
			if(managed_var_types[type] != undefined) {
				managed_var_types[type].reset($(this));
			}
			storage_exos.unset(this.id);
		});
		$('.placeholder_echange').remove();
		storage_exos.save();
		coloriser_les_lignes($("#p"+page_courante+" .mot"));
		// tempo
		var date = new Date();
		var curDate = null;
		dbug("reset loading");
		do { curDate = new Date(); } 
		while(curDate-date < 2000);
		$("#loading").hide();
	},100);
}
/*
	réglages globaux d'affichage des cahiers/exercices
*/
if(typeof(reglages_cahier_exos_ignorer_couleurs) == "undefined") {
	reglages_cahier_exos_ignorer_couleurs = storage_exos.getGlobal('reglages_cahier_exos_ignorer_couleurs');
}
//
//
$(function() {
	// initialiser les paramètres enregistrés du cahier
	// note: pas de save ça trompe la date de modification
	storage_exos.set('nom',$('title').html());
	// initialiser les variables
	$(".managed_var").each(function(){
		try {
			// récupérer son identifiant de storage
			var stid = this.id;
			// mémoriser sa valeur par défaut
			if($(this).data("mvt") == "champ") {
				$(this).data("defaut",$(this).html());
			}
			// vérifier si la variable existe
			if(typeof(storage_exos[stid]) == "object") {
				// selon les paramètres, configurer l'élément
				if(typeof(storage_exos[stid]['html']) != "undefined") {
					$(this).data("defaut",$(this).html());
					$(this).html(storage_exos[stid]['html']);
				}
				if(storage_exos[stid]['value']) {
					$(this).data("defaut",$(this).val());
					$(this).val(storage_exos[stid]['value']);
				}
				if(storage_exos[stid]['data']) { // pour les coches
					$(this).data("value",(storage_exos[stid]['data']));
				}
				if(storage_exos[stid]['pos']) { // pour les échanges
					var target = storage_exos[stid]['pos'];
					$(this).after('<span class="placeholder_echange '+stid+'" />');
					if($(".placeholder_echange."+target).length>0) {
						$(".placeholder_echange."+target).after(this);
					} else {
						$("#"+target).after(this);
					}
					$(this).data('pos',target);
				}
			}
		} catch(err) {
			// erreur dans le chargement de cette variable, po grave hein
		}
	});
	$('.placeholder_echange').remove();
	// boutons de fin
	$("#cahier_bouton_imprimer").click(function() {
		tout_imprimer();
	});
	$("#cahier_bouton_reset").click(function() {
		storage_exos.tout_reset();
	});
	$("#cahier_bouton_revenir").click(function() {
		window.location.reload();
	});
	$("#cahier_bouton_fermer").click(function() {
		if(window.history.length > 1) {
			window.history.back();
		} else {
			window.close();
		}
	});
});
/*
	système de colorisation
	appeler avec:
	
	coloriser_les_lignes($("#p"+page_courante+" .mot"))
*/
function coloriser_les_lignes(cibles) {
	var top0 = 0;
	var top = 0;
	var color = 0;
	//
	if(reglages_cahier_exos_ignorer_couleurs == "1") return;
	if(exo_en_cours && !exo_en_cours['appliquer_couleur_texte']) return;
	cibles.each(function() {
		if($(this).is(":visible")) {
			top = Math.floor($(this).position().top);
			if( Math.abs(top-top0) >10 ) {
				color++;
			}
			$(this).removeClass("color0 color1 color2").addClass("color"+(color%3));
			top0 = top;
		}
	});
}
var dimensionner_la_page = function(){
	$("#enonce").css({maxHeight:$(window).height()/3})
	$("#toutes_pages").height(
		$(window).height()
		-$("#enonce").outerHeight()
		-$("#bottom").outerHeight()
	);
	$("#p"+page_courante).width($("#toutes_pages").width()-8);
	$("#p"+page_courante).height($("#toutes_pages").height());
	coloriser_les_lignes($("#p"+page_courante+" .mot"));
};

/*
	système de pagination
*/
//var page_courante = 1;
//var total_pages = 1;
//var montre_page;
$(function() {
	total_pages = $('.page').length;
	/*
		système de pagination
	*/
	$("#bleft").click(function(){
		montre_page(page_courante-1);
		$(this).blur();
	});
	$("#bright").click(function(){
		montre_page(page_courante+1);
		$(this).blur();
	});
	$("#fleche").click(function() {
		montre_page(page_courante+1);
		$(this).blur();
	});
	montre_page = function(page) {
		var left;
		page = Number(page);
		if($("#p"+page).length>0 && page!=page_courante) {
			if(page_courante<page) {
				left = -1*$(window).width();
			} else {
				left = $(window).width();
			}
			var pc = page_courante;
			page_courante = page;
			// exo_en_cours paramètre global
			var exo = $("#p"+page).data("exo");
			if(exo in liste_exercices) {
				exo_en_cours = liste_exercices[exo];
			} else {
				exo_en_cours = null;
			}
			// fixer la largeur avant de déplacer la page courante
			// animer la page courante hors de vue et la cacher
			$("#p"+pc).queue(function(){
				$(this).width($("#toutes_pages").width()-8);
				$(this).height($("#toutes_pages").height());
				$(this).trigger("cacher");
				$(this).dequeue();
			})
			.animate({left:left},"normal",function(){
				$(this).hide();
			});
			// montrer et ramener en vue la nouvelle page
			// adapter automatiquement la largeur
			// (au cas où on change la taille de fenêtre)
			$("#p"+page).css({left:-1*left}).show().queue(function(){
				$(this).width($("#toutes_pages").width()-8);
				$(this).height($("#toutes_pages").height());
				$(this).dequeue();
			})
			.animate({left:0},"normal").queue(function(){
				$(this).dequeue();
				// NOTE: on queue le width auto pour être sûr qu'il ne s'execute
				// pas pendant un animate (si on clique plusieurs fois)
			});
			// la suite, après la fin des animations (en queue ?)
			// changer l'énoncé (vider si nécessaire)
			$("#enonce").attr("class",$("#enonce").data('classes'));
			if($("#p"+page+" div.enonce").length) {
				$("#enonce").html($("#p"+page+" div.enonce").html());
				if(exo_en_cours) $("#enonce").addClass(exo_en_cours.id_exo);
			}
			// à la dernière page, masquer la flêche -->
			if($("#p"+(page+1)).size() == 0) {
				$("#fleche").hide();
				$("#oups").hide();
			} else {
				$("#fleche").show();
				$("#oups").show();
			}
			// numéro de page (si existe)
			$(".cahier_pagenum").html(page);
			// actions à effectuer en montrant la page
			dimensionner_la_page();
			$("#p"+page).queue(function(){
				$("#p"+page).trigger("montrer");
				$(this).dequeue();
			})
		}
	}
	$(window).resize(dimensionner_la_page);
	//
	if(0 in liste_exercices) { exo_en_cours = liste_exercices[0]; }
	dimensionner_la_page();
	//
	dbug("fin loading cahiers.js");
	$("#loading").hide();
	$("#p1").trigger("montrer");
});
