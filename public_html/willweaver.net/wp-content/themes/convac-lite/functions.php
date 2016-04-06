<?php
/**
 * Convac functions and definitions.
 *
 * Sets up the theme and provides some helper functions, which are used in the
 * theme as custom template tags. Others are attached to action and filter
 * hooks in WordPress to change core functionality.
 *
 * When using a child theme (see http://codex.wordpress.org/Theme_Development
 * and http://codex.wordpress.org/Child_Themes), you can override certain
 * functions (those wrapped in a function_exists() call) by defining them first
 * in your child theme's functions.php file. The child theme's functions.php
 * file is included before the parent theme's file, so the child theme
 * functions would be used.
 *
 * Functions that are not pluggable (not wrapped in function_exists()) are
 * instead attached to a filter or action hook.
 *
 * For more information on hooks, actions, and filters,
 * see http://codex.wordpress.org/Plugin_API
 *
 */
/**
 * Registers widget areas.
 *
 */
function convac_lite_widgets_init() {
	register_sidebar(array(
		'name' => __('Page Sidebar', 'convac-lite'),
		'id' => 'page-sidebar',
		'before_widget' => '<li id="%1$s" class="ske-container %2$s">',
		'after_widget' => '</li>',
		'before_title' => '<h3 class="ske-title">',
		'after_title' => '</h3>',
	));
	register_sidebar(array(
		'name' => __('Blog Sidebar', 'convac-lite'),
		'id' => 'blog-sidebar',
		'before_widget' => '<li id="%1$s" class="ske-container %2$s">',
		'after_widget' => '</li>',
		'before_title' => '<h3 class="ske-title">',
		'after_title' => '</h3>',
	));
	register_sidebar(array(
		'name' => __('Footer Sidebar', 'convac-lite'),
		'id' => 'footer-sidebar',
		'before_widget' => '<div id="%1$s" class="ske-footer-container span3 ske-container %2$s">',
		'after_widget' => '</div>',
		'before_title' => '<h3 class="ske-title ske-footer-title">',
		'after_title' => '</h3>',
	));
}
add_action( 'widgets_init', 'convac_lite_widgets_init' );

/**
 * Sets up theme defaults and registers the various WordPress features that
 * Convac supports.
 *
 * @uses load_theme_textdomain() For translation/localization support.
 * @uses add_editor_style() To add Visual Editor stylesheets.
 * @uses add_theme_support() To add support for automatic feed links, post
 * formats, and post thumbnails.
 * @uses register_nav_menu() To add support for a navigation menu.
 * @uses set_post_thumbnail_size() To set a custom post thumbnail size.
 *
*/
function convac_lite_theme_setup() {
	/*
	 * Makes Convac available for translation.
	 *
	 * Translations can be added to the /languages/ directory.
	 * If you're building a theme based on Twenty Thirteen, use a find and
	 * replace to change 'convac-lite' to the name of your theme in all
	 * template files.
	 */
	 load_theme_textdomain( 'convac-lite', get_template_directory() . '/languages' );
	 
	// This theme styles the visual editor with editor-style.css to match the theme style.
	add_editor_style();

	add_theme_support( 'title-tag' );

	$pre_options = ( get_option('option_tree') != '' ) ? get_option( 'option_tree' ) : false ;
	if ( $pre_options) {
		$header_image = convac_lite_get_option( 'convac-lite_header_static_img' );
	} else {
		$header_image = get_template_directory_uri() . '/images/header-static-img.jpg';
	}


	add_theme_support( 'custom-header', array( 'flex-width' => true, 'width' => 1600, 'flex-height' => true, 'height' => 750, 'default-image' => $header_image ) );

	// This theme allows users to set a custom background.
	add_theme_support( 'custom-background', apply_filters( 'avis_custom_background_args', array('default-color' => 'ffffff', ) ) );

	/**
	* SETS UP THE CONTENT WIDTH VALUE BASED ON THE THEME'S DESIGN.
	*/
	global $content_width;
	if ( ! isset( $content_width ) ){
	      $content_width = 900;
	}

	 // Adds RSS feed links to <head> for posts and comments.
	add_theme_support( 'automatic-feed-links' );

	/*
	 * This theme uses a custom image size for featured images, displayed on
	 * "standard" posts and pages.
	 */
	add_theme_support('post-thumbnails');


	/**
	 * Enable support for Post Formats
	 */
	set_post_thumbnail_size( 636, 352, true );
	add_image_size( 'convac_lite_standard_img',636,352,true); 
	
	// This theme uses wp_nav_menu() in one location.
	register_nav_menus( array(
		'Header' => __( 'Main Navigation', 'convac-lite' ),
	));
}
add_action( 'after_setup_theme', 'convac_lite_theme_setup' ); 

/**
* Funtion to add CSS class to body
*/
function convac_lite_add_class( $classes ) {

	if ( 'page' == get_option( 'show_on_front' ) && ( '' != get_option( 'page_for_posts' ) ) && is_front_page() ) {
		$classes[] = 'front-page';
	}
	
	return $classes;
}
add_filter( 'body_class','convac_lite_add_class' );

/**
 * Filter content with empty post title
 *
 */

add_filter('the_title', 'convac_lite_untitled');
function convac_lite_untitled($title) {
	if ($title == '') {
		return __('Untitled','convac-lite');
	} else {
		return $title;
	}
}

// retrieves the attachment ID from the file URL
function convac_lite_get_image_id($image_url) {
	global $wpdb;
	$attachment = $wpdb->get_col($wpdb->prepare("SELECT ID FROM $wpdb->posts WHERE guid='%s';", $image_url )); 
    return $attachment[0]; 
}

function convac_lite_get_all_authors() {
	global $wpdb;
	$order = 'user_nicename';
	$user_ids = $wpdb->get_col("SELECT ID FROM $wpdb->users ORDER BY $order");

	foreach($user_ids as $user_id) :
		$user = get_userdata($user_id);
		if(count_user_posts( $user_id ) > 0) {
			$all_authors[] = array(
								'value' => $user_id,
								'label' => $user->display_name
							);
		}
	endforeach;
	return $all_authors;
}

/*---------------------------------------------------------------------------*/
/* ADMIN SCRIPT: Enqueue scripts in back-end
/*---------------------------------------------------------------------------*/
if( !function_exists('convac_lite_page_admin_enqueue_scripts') ){
    add_action('admin_print_scripts-appearance_page_ot-theme-options','convac_lite_page_admin_enqueue_scripts');
    /**
     * Register scripts for admin panel
     * @return void
     */
    function convac_lite_page_admin_enqueue_scripts(){	
		wp_enqueue_style( 'convac-lite-admin-stylesheet', get_template_directory_uri().'/SketchBoard/css/sketch-admin.css', false);
    }
}

/**
 * Add Customizer 
 */
require get_template_directory() . '/includes/customizer.php';

/**
 * Add Config File 
 */
require_once(get_template_directory() . '/SketchBoard/functions/admin-init.php');

/**
 * Add SkethThemes File 
 */
require_once(get_template_directory() . '/includes/sketchtheme-upsell.php');

/**
 * Get Option.
 *
 * Helper function to return the option value.
 * If no value has been saved, it returns $default.
 *
 * @param     string    The option ID.
 * @param     string    The default option value.
 * @return    mixed
 *
 * @access    public
 * @since     2.0
 */
if ( ! function_exists( 'convac_lite_get_option' ) ) {

  function convac_lite_get_option( $option_id, $default = '' ) {
    
    /* get the saved options */ 
    $options = get_option( 'option_tree' );
    

    /* look for the saved value */
    if ( isset( $options[$option_id] ) && '' != $options[$option_id] ) {

      return convac_lite_wpml_filter( $options, $option_id );
      
    }
    
    return $default;
    
  }
  
}


/**
 * Filter the return values through WPML
 *
 * @param     array     $options The current options    
 * @param     string    $option_id The option ID
 * @return    mixed
 *
 * @access    public
 * @since     2.1
 */
if ( ! function_exists( 'convac_lite_wpml_filter' ) ) {

  function convac_lite_wpml_filter( $options, $option_id ) {
      
    // Return translated strings using WMPL
    if ( function_exists('icl_t') ) {
      
      $settings = get_option('option_tree_settings');
      
      if ( isset( $settings['settings'] ) ) {
      
        foreach( $settings['settings'] as $setting ) {
          
          // List Item & Slider
          if ( $option_id == $setting['id'] && in_array( $setting['type'], array( 'list-item', 'slider' ) ) ) {
          
            foreach( $options[$option_id] as $key => $value ) {
          
              foreach( $value as $ckey => $cvalue ) {
                
                $id = $option_id . '_' . $ckey . '_' . $key;
                $_string = icl_t( 'Theme Options', $id, $cvalue );
                
                if ( ! empty( $_string ) ) {
                
                  $options[$option_id][$key][$ckey] = $_string;
                  
                }
                
              }
            
            }
          
          // All other acceptable option types
          } else if ( $option_id == $setting['id'] && in_array( $setting['type'], apply_filters( 'ot_wpml_option_types', array( 'text', 'textarea', 'textarea-simple' ) ) ) ) {
          
            $_string = icl_t( 'Theme Options', $option_id, $options[$option_id] );
            
            if ( ! empty( $_string ) ) {
            
              $options[$option_id] = $_string;
              
            }
            
          }
          
        }
      
      }
    
    }
    
    return $options[$option_id];
  
  }

}



$pre_options = ( get_option('option_tree') != '' ) ? get_option( 'option_tree' ) : false ;

if ( $pre_options) {

	add_action( 'wp_ajax_convac_lite_migrate_option', 'convac_lite_migrate_options' );
	add_action( 'wp_ajax_nopriv_convac_lite_migrate_option', 'convac_lite_migrate_options' );
	function convac_lite_migrate_options() {

		set_theme_mod('_colorpicker', convac_lite_get_option( 'convac-lite_colorpicker' ) );
		set_theme_mod('_show_pagination', convac_lite_get_option( 'convac-lite_show_pagination' ) );
		set_theme_mod('_logo_img', convac_lite_get_option( 'convac-lite_logo_img' ) );
		set_theme_mod('_moblie_menu', convac_lite_get_option( 'convac-lite_moblie_menu' ) );
		set_theme_mod('_headserach', convac_lite_get_option( 'convac-lite_headserach' ) );
		set_theme_mod('_author_img', convac_lite_get_option( 'convac-lite_author_img' ) );
		set_theme_mod('_author_name', convac_lite_get_option( 'convac-lite_author_name' ) );
		set_theme_mod('_author_desp', convac_lite_get_option( 'convac-lite_author_desp' ) );
		set_theme_mod('_sconnect_txt', convac_lite_get_option( 'convac-lite_sconnect_txt' ) );
		set_theme_mod('_fbook_link', convac_lite_get_option( 'convac-lite_fbook_link' ) );
		set_theme_mod('_twitter_link', convac_lite_get_option( 'convac-lite_twitter_link' ) );
		set_theme_mod('_gplus_link', convac_lite_get_option( 'convac-lite_gplus_link' ) );
		set_theme_mod('_linkedin_link', convac_lite_get_option( 'convac-lite_linkedin_link' ) );
		set_theme_mod('_pinterest_link', convac_lite_get_option( 'convac-lite_pinterest_link' ) );
		set_theme_mod('_flickr_link', convac_lite_get_option( 'convac-lite_flickr_link' ) );
		set_theme_mod('_foursquare_link', convac_lite_get_option( 'convac-lite_foursquare_link' ) );
		set_theme_mod('_youtube_link', convac_lite_get_option( 'convac-lite_youtube_link' ) );
		set_theme_mod('_innerpage_img', convac_lite_get_option( 'convac-lite_innerpage_img' ) );
		set_theme_mod('_blogpage_heading', convac_lite_get_option( 'convac-lite_blogpage_heading' ) );
		set_theme_mod('_copyright', convac_lite_get_option( 'convac-lite_copyright' ) );
		
		delete_option( 'option_tree' );
		delete_option( 'option_tree_settings' );

		echo __('All the settings migrated successfully.', 'convac-lite');
		
		die();

	}

	add_action('admin_menu', 'convac_lite_migrate_menu');
	function convac_lite_migrate_menu() {
		add_theme_page( __('Migrate Options', 'convac-lite'), __('Migrate Options', 'convac-lite'), 'administrator', 'sktmigrate', 'convac_lite_migrate_menu_options' );
	}

	function convac_lite_migrate_menu_options() { ?>
		<h1><?php _e('Migrate Settings to Customizer', 'convac-lite') ?></h1>
		<p><?php _e('As per the new WordPress guidelines it is required to use the Customizer for implementing theme options.', 'convac-lite'); ?></p>
		<p><?php _e('So, click on this button to migrate all data from previous version.', 'convac-lite'); ?></p>
		<p><strong><?php _e('Note: only click this option once immidiatly after upgrade. Do not press back or refresh button while migrating...', 'convac-lite'); ?></strong></p>
		<button id="convac-migrate-btn" class="button button-primary"><?php _e( 'Migrate to Customizer', 'convac-lite' ); ?></button>
		<script type="text/javascript">
		jQuery(document).ready(function(){
			'use strict';
			jQuery('#convac-migrate-btn').click(function() {
				jQuery('body').append('<div id="migrate-div" style="position:absolute;left:0;top:0;bottom:0;right:0;background-color:rgba(255,255,255,0.7);"><img style="position:absolute;top:50%;left:50%;" class="migrate-loader" src="<?php echo get_template_directory_uri()."/images/loader.gif"; ?>" alt="<?php _e("Loading", "convac-lite"); ?>"></div>');
			    jQuery.ajax({
			        url: "<?php echo home_url('/');?>wp-admin/admin-ajax.php",
			        type: 'POST',
			        data: { action: 'convac_lite_migrate_option' },
			        success: function( response ) {
			        	jQuery('#migrate-div').remove();
			            alert( response );
			            var wp_adminurl = "<?php echo esc_url( home_url('/') ).'wp-admin/customize.php'; ?>";
	  					jQuery(location).attr("href", wp_adminurl);
			        }
			    });
				return false;

			});
		});
		</script>
	<?php }
} ?>