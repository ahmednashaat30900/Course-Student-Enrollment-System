var tags=[];
            init();
            function init(){
                var w = $(".item").not(".item-with-desc").width();
                var c= $(".sde-courses .container").width();
                var items_row = Math.floor(c/w);

                $(".item").not(".item-with-desc").not(".course-hidden").each(function(index){
                    $(this).css("order", Math.ceil((index+1) / items_row)*2 -1 );
                });
            }

            $(".item").not(".item-with-desc").click(function(){
                var order = parseInt($(this).css("order")) + 1;
                console.log("order: "+order);
                $(".item-with-desc").css("order", order);

                var nome = $(this).find(".course-name").text();
                var resumo = $(this).data("summary");
                var objectivos = $(this).data("goals");

                funUpdateCourseInfo(nome, resumo, objectivos);
                $(".item-with-desc").removeClass("hide-info").removeClass("hidden");
                $(".item").not(".item-with-desc").addClass("inactive");
                $(this).removeClass("inactive");
                $('html, body').animate({
                    scrollTop: $(this).offset().top - 50
                });
            });

            $(".item-with-desc .close").click(function(){
                $(".item").not(".item-with-desc").removeClass("inactive");
                $(".item-with-desc").addClass("hide-info");
                setTimeout(function(){ $(".item-with-desc").addClass("hidden"); }, 1500);
            });

            $('.courses-parent .item a').click(function(e){
                e.preventDefault();
                /*setTimeout(function(){ $('html, body').animate({
                    scrollTop: $(".item-with-desc").offset().top - 50
                }, 1200); }, 300);*/
            });


            function funUpdateCourseInfo( nome, resumo, objectivos){
                $(".item-with-desc").find(".course-name").text(nome);
                $(".item-with-desc").find(".course-summary").text(resumo);
                $(".item-with-desc").find(".course-goals").html(objectivos);
            }

            $( window ).resize(function() {
              init();
            });


            $(".checkbutton").click(function(){
                $(this).toggleClass("selected");
                if (this.className.includes("selected")== true){
                    if (tags.indexOf(this.id) == -1) tags.push(this.id);
                }
                else{
                    var j= tags.indexOf(this.id);
                    tags.splice(j, 1);
                }
                filterSelection();
            });


            function clearFilters(){
                $(".checkbutton").removeClass("selected");
                tags=[];
                filterSelection();
            }


            filterSelection();

            function filterSelection(){
                //actualiza a lista de tags
                /*var actual_filters =  document.querySelectorAll('.checkbutton.selected');
                actual_filters.forEach(function(element){
                    tags.push(element.id);
                });
                console.log(tags);*/

                //verifica quais os elementos que nao possuem as tags e esconde-os
                const cursos = Array.from(document.querySelectorAll('.item:not(.item-with-desc)'));
                var classes;
                cursos.forEach(function(curso){
                    classes = curso.className;
                    var hidden= false;
                    if ( classes.indexOf("course-hidden") >= 0 ) hidden = true;

                    var a = classes.split(" ");
                    var r = getMatch(a, tags);
                    if (tags.length >0 && r.length == 0 && !hidden){
                        curso.className = classes + " course-hidden";
                    }
                    else{
                        curso.className = classes.replace('course-hidden', '');
                    }

                });
                init();
            }

            function getMatch(a, b) {
                var matches = [];
                for ( var i = 0; i < a.length; i++ ) {
                    for ( var e = 0; e < b.length; e++ ) {
                        if ( a[i] === b[e] ) matches.push( a[i] );
                    }
                }
                return matches;
            }