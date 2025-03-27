var exo_champ_echange = null;
//
function colorer_nombre(num) {
	if(num == "") return "";
	var classe = ["unite","dizaine","centaine"];
	var out = "";
	var nm,nf,i;
	var spl = num.split(/(\d[\d,]*)/);
	for(bl in spl) {
		i=0;
		nf = "";
		nm = spl[bl];
		if(nm.match(/^\d[\d,]*$/)) {
			var mm = nm.match(/^(.*?),(.*)$/);
			if(mm) {
				nm = mm[1];
				nf = '<span class="milliers">,'+mm[2]+"<\/span>";
			}
			var oo = "";
			for(j=nm.length-1; j>=0; j--) {
				if(nm[j].match(/\d/)) {
					if(i<3) cl=classe[i]; else cl="milliers";
					oo = '<span class="' + cl + '">'
					+ nm[j] + "<\/span>" + oo;
					i++;
				} else {
					i=0;
					oo = nm[j]+oo;
				}
			}
			out = out + oo + nf;
		} else {
			out = out + spl[bl];
		}
	}
	return out;
}
//
function print_blocs(blocs,conteneur) {
	$(blocs).children(".mot, .space, br, .operation_posee, .fraction, span" ).each(function(){
		$(this).find(".clavier_interactif").remove();
		if($(this).is(".champ_qcm")) {
			conteneur.append('<span class="boite">' +$(this).find(".managed_var").html() +'</span>');
		} else if($(this).is(".champ")) {
			var txt = $(this).html();
			if(txt == "") txt="&nbsp;&nbsp;&nbsp;&nbsp;";
			conteneur.append('<span class="stu">'+txt +'</span>');
		} else if($(this).parents(".coche").length>0) {
			var cl = $(this).parents(".coche").attr("class").match(/(sel\d)/);
			if(cl) cl = cl[0]; else cl = "";
			conteneur.append('<span class="'+cl+'">' +$(this).html() +'</span>');
		} else if($(this).is('.operation_posee')) {
			var ope = $(this).clone();
			ope.find('input').attr("readonly","readonly");
			conteneur.append(ope);
		} else if($(this).is('.ctn')) {
			var contbis = $("<span/>");
			contbis.addClass($(this).attr("class"));
			print_blocs($(this),contbis);
			conteneur.append(contbis);
		} else {
			var ope = $(this).clone();
			conteneur.append(ope);
		}
	});
}
print_exo_defaut = function(id_exo,conteneur) {
	$(".page."+id_exo+" .contenu_page").each(function(){
		print_blocs($(this),conteneur);
		conteneur.append("<br/>");
	});
	$(conteneur).find('.champ').each(function(){
		var txt = $(this).html();
		if(txt == "") txt="&nbsp;&nbsp;&nbsp;&nbsp;";
		$(this).replaceWith('<span class="stu">'+txt +'</span>');
	});
}
/*
	gestion de focus / claviers
*/
function unfocus_all(sauf) {
	window.getSelection().removeAllRanges();
	$(".clavier_interactif").not('.clavier_nohide').hide();
	$('.focus').removeClass('focus');
	exo_champ_echange = null;
}
function doc_mouse_down() {
	var mousedown = function(){
		$(this).unbind("mousedown",mousedown);
		unfocus_all();
	};
	$(document).bind("mousedown",mousedown);
}
/*
	afficher un clavier QCM
*/
function clavier_qcm(qcm, adapte_hauteur) {
	if(typeof(adapte_hauteur) == "undefined") adapte_hauteur = true;
	var gpm = qcm.find(".qcm_menu");
	var btn = qcm.find(".qcm_bouton");
	// position centrée en largeur
	var left = (btn.width() - gpm.width())/2;
	if(btn.offset().left + left + gpm.width() > $(window).width() - 40) {
		left = $(window).width() - 40 - btn.offset().left - gpm.width();
	}
	if(btn.offset().left + left < 40) {
		left = 40 - btn.offset().left;
	}
	gpm.css({left:Math.floor(left), right:"auto"});
	// position adaptée en hauteur
	if(adapte_hauteur &&
	btn.offset().top > $(window).height()*2/3) {
		gpm.css({bottom:(btn.outerHeight()+4)+"px"});
	} else {
		gpm.css({top:(btn.outerHeight()+7)+"px"});
	}
	gpm.show();
}
/*
	champs texte
*/
function champ_texte_get_pos(that) {
	// Safari n'a pas toujours une range vide par défaut
	var range_count = window.getSelection().rangeCount
	if(range_count > 0) {
		// récupération de la position du curseur dans le champ
		// (si il y est)
		var range = window.getSelection().getRangeAt(0);
		var TN = $(that).children().andSelf().textNodes();
		var TT=0;
		for(i=0; i<TN.length; i++) {
			if(TN[i] == range.startContainer) {
				break;
			}
			TT += TN[i].length;
		}
		return TT+range.startOffset;
	}
	return 0;
}
function champ_texte_set_pos(that,navant) {
	// récupération du nouveau node correspondant
	// à la position précédente du curseur
	var TN = $(that).children().andSelf().textNodes();
	var TT = 0;
	if(TN.length>0) {
		TT=0;
		for(i=0; i<TN.length; i++) {
			if(TT+TN[i].length>navant) {
				break;
			}
			TT += TN[i].length;
		}
		if(i==TN.length) { --i; TT=TT-TN[i].length; }
	} else {
		TT=navant;
		i=0;
		TN=[that];
	}
	// créer un nouveau range pour y positionner le curseur
	var nrange = document.createRange();
	try {
		nrange.setStart(TN[i],navant-TT);
		nrange.setEnd(TN[i],navant-TT);
	} catch(e) {
		nrange.setStart(TN[i],TN[i].length);
		nrange.setEnd(TN[i],TN[i].length);
	}
	//
	window.getSelection().addRange(nrange);
}
function op_spaces(texte) {
	var out = texte.replace(/ *([-+=()x×:]) */ig,' $1 ')
	out = out.replace(/x/ig,'×')
	return out;
}
function champ_texte_update(that,event,_content,_pos) {
	// position actuelle
	var navant;
	if(typeof(_pos)!="undefined") navant = _pos;
	else navant = champ_texte_get_pos(that);
	// contenu du champ
	var content;
	if(typeof(_content)!="undefined") content = _content;
	else content = $(that).html().replace(/<[^><]+>/g,"");
	//
	var len = content.length;
	// gérer les opérations (limiter aux numériques)
	if($(that).is(".champ_numerique")) {
		// on met des espaces avant et après les symboles
		var navant = op_spaces(content.slice(0,navant)).length;
		content = op_spaces(content);
	}
	// on met les couleurs
	content = colorer_nombre(content);
	//
	$(that).html(content);
	window.getSelection().removeAllRanges();
	//
	champ_texte_set_pos(that,navant);
	//
	$(that).css({
		paddingLeft:Math.max(5,30-5*len)+"px",
		paddingRight:Math.max(5,30-5*len)+"px",
	});
	//
	storage_exos.set(that.id,{html:$(that).html()});
	storage_exos.save();
	//
	coloriser_les_lignes($("#p"+page_courante+" .mot"));
	try {
		event.preventDefault();
	} catch(er) {
	}
}
/*
	clavier numérique
	si il n'y en a qu'un dans la page courante ("montrer")
	-> sélectionner de force celui-là
*/
function clavier_numerique(that) {
	//
	var clav = $(that).data('clavier');
	if(!clav) {
		clav = $('<div class="clavier_interactif clavier_num_div"></div>');
		clav.css({position:"absolute", top:"-100px", left:"0px", display:"none"});
		var btn;
		// fonction d'ajout d'un caractère
		var doclick = function(e) {
			var cible = $(that);
			cible.focus();
			var pos = champ_texte_get_pos(cible);
			var content = cible.html().replace(/<[^><]+>/g,"");
			content = content.slice(0,pos)+$(this).val()+content.slice(pos);
			pos = pos + $(this).val().length;
			champ_texte_update(cible[0],0,content,pos);

			cible.focus();
			stopPropa(e);
			return false;
		};
		// nombres
		for(k=0;k<10;k++) {
			btn = $('<button value="' +k +'">' +k +'</button>');
			btn.bind("click",doclick).mousedown(function(e){ stopPropa(e); });
			clav.append(btn);
		}
		// virgule
		btn = $('<button value=",">,</button>');
		btn.bind("click",doclick).mousedown(function(e){ stopPropa(e); });
		clav.append(btn);
		// gomme
		btn = $('<button value=""><img src="communs/gomme_medium.png" /></button>');
		btn.bind("click",function(e){
			var cible = $(that);
			cible.html("");
			champ_texte_update(cible[0],0);
			cible.focus();
			stopPropa(e);
			return false;
		}).mousedown(function(e){ stopPropa(e); });
		clav.append(btn);
		// boutons supplémentaires
		if($(that).is('.champ_numerique_plus')) {
			clav.append('<br/>');
			var symboles = ["(",")","+","-","×",":","="];
			for(i=0; i<symboles.length; i++) {
				btn = $('<button value="' +symboles[i]+ '">' +symboles[i]+ '</button>');
				btn.bind("click",doclick).mousedown(function(e){ stopPropa(e); });
				clav.append(btn);
			}
		}
		// bouton supplémentaire: effacement
		if($(that).is('.champ_numerique_plus')) {
			btn = $('<button value="">&larr;</button>');
			btn.bind("click",function(e) {
				var cible = $(that);
				cible.focus();
				var content = cible.html().replace(/<[^><]+>/g,"");//+$(this).val();
				var pos = champ_texte_get_pos(cible);
				var pos_origine = pos;

				while(content.substr(pos-1,1) == " " && pos > 0) pos--;
				pos = Math.max(pos-1,0);
				content = content.slice(0,pos)+content.slice(pos_origine);
				champ_texte_update(cible[0],0,content,pos);
				
				cible.focus();
				stopPropa(e);
				return false;
			}).mousedown(function(e){ stopPropa(e); });
			clav.append(btn);
		}
		//
		$(document.body).append(clav);
		$(that).data('clavier',clav);
	}
	//
	var width = clav.outerWidth();
	//var left = Math.floor($(that).offset().left + $(that).width()/2 - width/2);
	var left = Math.floor($(that).offset().left + 30 - width/2);
	var top = Math.floor($(that).offset().top+$(that).outerHeight()) +5;
// 				if(top>$(document).height()*2/3) {
// 					top = Math.floor($(that).offset().top 
//					-$(clav).outerHeight()) -5;
// 				}
	if(left+width>$(document).width()-40) {
		left = Math.floor($(document).width()-width-40);
	} else if(left <40) {
		left = 40;
	}
	clav.css({
		left: left+"px",
		top: top+"px",
		position:"absolute"
	}).show();
}
//
$(function() {
	/*
		boutons à choix multiple
	*/
	// cliquer sur un trou dans le texte
	// fait apparaitre le menu de choix multiple
	$(".champ_qcm .qcm_bouton").click(function(e){
		var qcm = $(this).parents('.champ_qcm');
		unfocus_all();
		//
		clavier_qcm(qcm);
		//
		qcm.addClass("focus");
		//$(".qcm_bouton").not(this).addClass("noborder");
		doc_mouse_down()
		stopPropa(e);
	});
	// cliquer sur un bouton du menu de choix multiple
	// cache le menu, affiche et enregistre la réponse
	$("button.qcm_bouton_choix").click(function(e){
		window.getSelection().removeAllRanges();
		$(this).blur();
		//
		var numero_du_trou = $(this).val();
		var cible = $("#"+numero_du_trou);
		cible.html($(this).html());
		//
		unfocus_all();
		//
		coloriser_les_lignes($("#p"+page_courante+" .mot"));
		// cookie
		storage_exos.set(cible.attr('id'),{html:$(this).html()});
		storage_exos.save();
		stopPropa(e);
	}).mousedown(function(e){ stopPropa(e); });
	/*
		champs cochables
	*/
	$(".coche").click(function(e){
		window.getSelection().removeAllRanges();
		//
		var coche = $(this).data("value");
		if(coche == null) coche=0;
		//
		var m = $(this).attr("class").match(/(\d)colors/);
		maxcoches = Number(m[1]);
		if( !(maxcoches>0 && maxcoches<10) ) maxcoches = 3;
		//
		coche = (coche+1) % maxcoches;
		$(this).data("value",coche);
		//
		storage_exos.set(this.id,{data:coche});
		storage_exos.save();
		//
		$(this).removeClass("sel0 sel1 sel2 sel3 sel4 sel5 sel6 sel7 sel8 sel9").addClass("sel"+coche);
		//
		stopPropa(e);
	}).each(function(){
		var coche = $(this).data("value");
		if(coche == null) coche=0;
		$(this).removeClass("sel0 sel1 sel2 sel3 sel4 sel5 sel6 sel7 sel8 sel9").addClass("sel"+coche);
	});
	/*
		champs echangeables
	*/
	exo_champ_echange = null;
	$(".echange").click(function(){
		//
		if(exo_champ_echange == null) {
			unfocus_all();
			$(this).addClass("focus");
			exo_champ_echange = $(this);
		} else {
			// vérfier qu'on a le droit de faire l'échange (même page)
			var page1 = $(this).parents(".page").attr("id");
			var page2 = $(exo_champ_echange).parents(".page").attr("id");
			if(page1 == page2) {
				var placeholder = $("<span id='placeholder' />");
				var exo_ce_champ = $(this);
				//
				exo_ce_champ.after(placeholder);
				exo_champ_echange.after(exo_ce_champ);
				placeholder.after(exo_champ_echange);
				placeholder.remove();
				// échanger les valeurs de position originales
				var eccpos;
				if(exo_ce_champ.data('pos')) {
					eccpos = exo_ce_champ.data('pos');
				} else {
					eccpos = exo_ce_champ.attr('id');
				}
				if(exo_champ_echange.data('pos')) {
					exo_ce_champ.data('pos',exo_champ_echange.data('pos'));
				} else {
					exo_ce_champ.data('pos',exo_champ_echange.attr('id'));
				}
				exo_champ_echange.data('pos',eccpos);
				// enregistrer les pos originales
				storage_exos.set(exo_ce_champ.attr('id'), {pos:exo_ce_champ.data('pos')});
				storage_exos.set(exo_champ_echange.attr('id'), {pos:exo_champ_echange.data('pos')});
				storage_exos.save();
				//
				exo_champ_echange.removeClass("focus");
 				exo_champ_echange = null;
				coloriser_les_lignes($("#p"+page_courante+" .mot"));
			} else {
				exo_champ_echange.removeClass("focus");
				$(this).addClass("focus");
				exo_champ_echange = $(this);
			}
		}
	});
	/*
		champs texte
	*/
	$(".champ").bind("keyup",function(event){
		return champ_texte_update(this,event);
	}).bind("keypress",function(event){
		if(event.keyCode == 13) { return false; }
		var content = $(this).html().replace(/<[^><]+>/g,"");
		var len = content.length;
		$(this).css({
			paddingLeft:Math.max(5,30-5*len)+"px",
			paddingRight:Math.max(5,30-5*len)+"px",
		});
	}).bind("focus",function(){
		// TODO: && c'est pas un nohide ?
		if($(this).is('.champ_numerique')) {
			var pos = champ_texte_get_pos(this);
			unfocus_all();
			clavier_numerique(this);
			doc_mouse_down()
			champ_texte_set_pos(this,pos);
		} else {
			var pos = champ_texte_get_pos(this);
			unfocus_all();
			champ_texte_set_pos(this,pos);
		}
	}).bind("mousedown",function(e){
		if($(this).is('.champ_numerique')) {
			clavier_numerique(this);
			doc_mouse_down()
		}
		stopPropa(e);
	}).bind("click",function(e){
		stopPropa(e);
	});
	/*
		champs des opérations posées
	*/
	$('.operation_posee input').bind("keyup",function(){
		storage_exos.set($(this).attr("id"), {value:$(this).val()});
		storage_exos.save();
	});
});
/*
	triggers
*/
$(".page").live("cacher",function(){
	$('.clavier_interactif').hide();
});
$(".page").live("montrer",function(){
	if(exo_champ_echange != null) {
		exo_champ_echange.removeClass("focus");
		exo_champ_echange = null;
	}
	$(this).find(".champ").each(function() {
		var content = $(this).html().replace(/<[^><]+>/g,"");
		var len = content.length;
		$(this).css({
			paddingLeft:Math.max(5,30-5*len)+"px",
			paddingRight:Math.max(5,30-5*len)+"px",
		});
		//
		$(this).html(colorer_nombre(content));
	});
	// rebelote, car le précédent modifie des trucs
	coloriser_les_lignes($("#p"+page_courante+" .mot"));
	// montrer les choix multiples et claviers nums seuls sur leur page
	var champs = $(this).find(".champ_qcm, .champ_numerique, .champ");
	if(champs.length == 1) {
		if(champs.not(".champ_noshow").is(".champ_numerique")) {
			clavier_numerique(champs);
			champs.data('clavier').addClass('clavier_nohide');
		}
	}
	// montrer les choix multiples et claviers nums seuls sur leur ligne
	// ou pas
	if($(this).is(".montrer_tout")) {
		$(this).find(".champ_qcm").each(function() {
			clavier_qcm($(this),false);
			$(this).find(".qcm_menu").addClass('clavier_nohide');
		});
	}
	//
	// ci dessous: fin de bind('montrer')
});
