/* ------------------------------------- */
/*  TABLE OF CONTENTS
 /* ------------------------------------- */
/*   PRE LOADING                          */
/*   WOW                                 */
/*   Menu                                */
/*  STICKY HEADER                        */
/*   COUNTER                             */
/*   portfolio-filter                    */
/*   pop up                              */
/*   OWL CAROUSEL                        */
/*    MAPS                               */
/*  TEXT ANIMATE                         */
/*   TEXT ROTATOR                        *



/*--------------------------------------------*/
/*  PRE LOADING
 /*------------------------------------------*/
'use strict';
$(window).on('load', function () {
    $('.loader').delay(500).fadeOut('slow');
});


$(document).ready(function() {

    'use strict';
    /* ------------------------------------- */
    /*   wow
     /* ------------------------------------- */
    var wow = new WOW(
        {
            animateClass: 'animated',
            offset: 10,
            mobile: true
        }
    );
    wow.init();

    /* ==============================================
     Smooth Scroll To Anchor
     =============================================== */



     $('.nav-link').on('click', function(e){
         if (window.matchMedia('(max-width: 767px)').matches){
                e.preventDefault();
                // $(this).next($('.sub_menu')).slideToggle();
                $(this).next($('.multi_col')).slideToggle();
            }
     });
    $('.navbar-nav a').on('click', function (event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });

    /* ==============================================
     STICKY HEADER
     =============================================== */

    $(window).on('scroll', function () {
        if ($(window).scrollTop() < 100) {
            $('.header').removeClass('sticky_header');
        } else {
            $('.header').addClass('sticky_header');
        }
    });


    /* ------------------------------------- */
    /* Animated progress bars
     /* ------------------------------------- */

    $('.single_progressbar').waypoint(function () {
        $('.progress-bar').progressbar({
            transition_delay: 500
        });
    }, {
        offset: '100%'
    });

    /* --------------------------------------------------------
     COUNTER JS
     ----------------------------------------------------------- */

    $('.counter').counterUp({
        delay: 5,
        time: 3000
    });



    /* ==============================================
     pop up
     =============================================== */

    // portfolio-pop up

    $('.portfolio').magnificPopup({
        delegate: 'a',
        type: 'image',
        tLoading: 'Loading image #%curr%...',
        mainClass: 'mfp-img-mobile',
        gallery: {
            enabled: true,
            navigateByImgClick: true,
            preload: [0,1] // Will preload 0 - before current, and 1 after the current image
        },
        image: {
            tError: '<a href="%url%">The image #%curr%</a> could not be loaded.',
            titleSrc: function(item) {
                return item.el.attr('title');
            }
        },
        zoom: {
            enabled: true,
            duration: 300, // don't foget to change the duration also in CSS
            opener: function (element) {
                return element.find('img');
            }
        }
    });

    $('.popup_video').magnificPopup({
        disableOn: 700,
        type: 'iframe',
        mainClass: 'mfp-fade',
        removalDelay: 160,
        preloader: false,
        fixedContentPos: false
    });
    /* ==============================================
     OWL CAROUSEL
     =============================================== */
    $(".hero_carousel").owlCarousel({
        loop:true,
        autoplay:true,
        smartSpeed:550,
        autoplayHoverPause:false,
        dots:true,
        nav:false,
        responsiveClass:true,
        items:1,
        animateOut: 'fadeOut',
        animateIn: 'fadeIn'
    });
    $(".team_carousel").owlCarousel({
        loop:true,
        autoplay:true,
        smartSpeed:450,
        autoplayHoverPause:false,
        dots:false,
        nav:false,
        responsiveClass:true,
        responsive:{
            0:{
                items:1
            },
            500:{
                items:2

            },
            1000:{
                items:3

            },
            1200:{
                items:4

            }
        },
        items:4
    });
    $(".testimonial_carousel_one").owlCarousel({
        loop:true,
        autoplay:true,
        smartSpeed:550,
        autoplayHoverPause:false,
        dots:true,
        nav:false,
        responsiveClass:true,
        items:1
    });
    $(".testimonial_carousel_two").owlCarousel({
        loop:true,
        autoplay:true,
        smartSpeed:550,
        autoplayHoverPause:false,
        dots:false,
        nav:false,
        responsiveClass:true,
        responsive:{
            0:{
                items:1
            },
            450:{
                items:1

            },
            800:{
                items:2

            }
        },
        items:2
    });
    $(".testimonial_carousel_three").owlCarousel({
        loop:true,
        autoplay:true,
        smartSpeed:550,
        autoplayHoverPause:false,
        dots:false,
        nav:false,
        responsiveClass:true,
        responsive:{
            0:{
                items:1
            },
            450:{
                items:1

            },
            800:{
                items:2

            },
            1200:{
                items:3
            }
        },
        items:3
    });
    $(".blog_carousel").owlCarousel({
        loop:true,
        autoplay:true,
        smartSpeed:450,
        autoplayHoverPause:false,
        dots:false,
        nav:false,
        responsiveClass:true,
        responsive:{
            0:{
                items:1
            },
            450:{
                items:1

            },
            800:{
                items:2

            },
            1200:{
                items:3

            }
        },
        items:3
    });
    $(".brand_carousel").owlCarousel({
        loop:true,
        autoplay:true,
        smartSpeed:450,
        autoplayHoverPause:false,
        dots:false,
        nav:false,
        responsiveClass:true,
        responsive:{
            0:{
                items:2
            },
            600:{
                items:3

            },
            1000:{
                items:5

            }
        },
        items:5
    });
    $(".screen_carousel").owlCarousel({
        loop:true,
        autoplay:true,
        smartSpeed:450,
        autoplayHoverPause:false,
        dots:true,
        nav:false,
        responsiveClass:true,
        responsive:{
            0:{
                items:1
            },
            500:{
                items:2

            },
            1000:{
                items:4
            }
        },
        items:4
    });

    if($("#typed").length > 0){
        var typed = new Typed('#typed', {
            stringsElement: '#typed-strings',
            typeSpeed: 100,
            loop: true
        });
    }
});