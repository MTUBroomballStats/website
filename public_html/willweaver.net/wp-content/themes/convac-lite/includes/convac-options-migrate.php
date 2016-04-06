<?php 

add_action( 'wp_ajax_convac_lite_migrate_option', 'convac_lite_migrate_options' );
add_action( 'wp_ajax_nopriv_convac_lite_migrate_option', 'convac_lite_migrate_options' );
function convac_lite_migrate_options() {

	$convac_lite_pre_options = get_option( 'convac_lite' );

	set_theme_mod( 'convac_lite_pri_color', $convac_lite_pre_options['convac_colorpicker'] );
	set_theme_mod( 'convac_lite_headerbg_color', $convac_lite_pre_options['convac_headercolorpicker'] );
	set_theme_mod( 'convac_lite_navfont_color', $convac_lite_pre_options['convac_navfontcolorpicker'] );

	set_theme_mod( 'convac_lite_logo_img', $convac_lite_pre_options['convac_logo_img'] );
	set_theme_mod( 'site_icon', $convac_lite_pre_options['convac_favicon'] );

	if( $convac_lite_pre_options['convac_hide_featured_box'] == 'true' )
		set_theme_mod( 'home_feature_sec', 'on' );
	else
		set_theme_mod( 'home_feature_sec', 'off' );

	set_theme_mod( 'first_feature_heading', $convac_lite_pre_options['convac_fb1_first_part_heading'] );
	set_theme_mod( 'first_feature_image', $convac_lite_pre_options['convac_fb1_first_part_image'] );
	set_theme_mod( 'first_feature_content', $convac_lite_pre_options['convac_fb1_first_part_content'] );
	set_theme_mod( 'first_feature_link', $convac_lite_pre_options['convac_fb1_first_part_link'] );
	set_theme_mod( 'second_feature_heading', $convac_lite_pre_options['convac_fb2_second_part_heading'] );
	set_theme_mod( 'second_feature_image', $convac_lite_pre_options['convac_fb2_second_part_image'] );
	set_theme_mod( 'second_feature_content', $convac_lite_pre_options['convac_fb2_second_part_content'] );
	set_theme_mod( 'second_feature_link', $convac_lite_pre_options['convac_fb2_second_part_link'] );
	set_theme_mod( 'third_feature_heading', $convac_lite_pre_options['convac_fb3_third_part_heading'] );
	set_theme_mod( 'third_feature_image', $convac_lite_pre_options['convac_fb3_third_part_image'] );
	set_theme_mod( 'third_feature_content', $convac_lite_pre_options['convac_fb3_third_part_content'] );
	set_theme_mod( 'third_feature_link', $convac_lite_pre_options['convac_fb3_third_part_link'] );
	
	if( $convac_lite_pre_options['convac_hide_callto_action'] == 'true' )
		set_theme_mod( 'home_cta_sec', 'on' );
	else
		set_theme_mod( 'home_cta_sec', 'off' );

	set_theme_mod( 'home_cta_heading', $convac_lite_pre_options['convac_catoac_heading'] );
	set_theme_mod( 'home_cta_content', $convac_lite_pre_options['convac_catoac_content'] );
	set_theme_mod( 'home_cta_btn_txt', $convac_lite_pre_options['convac_catoac_txt'] );
	set_theme_mod( 'home_cta_btn_link', $convac_lite_pre_options['convac_catoac_link'] );
	
	if( $convac_lite_pre_options['convac_hide_parallax'] == 'true' )
		set_theme_mod( 'home_parallax_sec', 'on' );
	else
		set_theme_mod( 'home_parallax_sec', 'off' );

	set_theme_mod( 'parallax_image', $convac_lite_pre_options['convac_fullparallax_image'] );
	set_theme_mod( 'parallax_content', $convac_lite_pre_options['convac_para_content_left'] );
	
	if( $convac_lite_pre_options['convac_hide_home_blog'] == 'true' )
		set_theme_mod( 'home_blog_sec', 'on' );
	else
		set_theme_mod( 'home_blog_sec', 'off' );

	set_theme_mod( 'home_blog_title', $convac_lite_pre_options['convac_blogsec_title'] );
	set_theme_mod( 'home_blog_num', $convac_lite_pre_options['convac_blog_no'] );
	

	if( $convac_lite_pre_options['convac_hide_client_logo'] == 'true' )
		set_theme_mod( 'home_brand_sec', 'on' );
	else
		set_theme_mod( 'home_brand_sec', 'off' );

	set_theme_mod( 'home_brand_sec_title', $convac_lite_pre_options['convac_clientsec_title'] );
	set_theme_mod( 'brand1_alt', $convac_lite_pre_options['convac_img1_title'] );
	set_theme_mod( 'brand1_img', $convac_lite_pre_options['convac_img1_icon'] );
	set_theme_mod( 'brand1_url', $convac_lite_pre_options['convac_img1_link'] );
	set_theme_mod( 'brand2_alt', $convac_lite_pre_options['convac_img2_title'] );
	set_theme_mod( 'brand2_img', $convac_lite_pre_options['convac_img2_icon'] );
	set_theme_mod( 'brand2_url', $convac_lite_pre_options['convac_img2_link'] );
	set_theme_mod( 'brand3_alt', $convac_lite_pre_options['convac_img3_title'] );
	set_theme_mod( 'brand3_img', $convac_lite_pre_options['convac_img3_icon'] );
	set_theme_mod( 'brand3_url', $convac_lite_pre_options['convac_img3_link'] );
	set_theme_mod( 'brand4_alt', $convac_lite_pre_options['convac_img4_title'] );
	set_theme_mod( 'brand4_img', $convac_lite_pre_options['convac_img4_icon'] );
	set_theme_mod( 'brand4_url', $convac_lite_pre_options['convac_img4_link'] );
	set_theme_mod( 'brand5_alt', $convac_lite_pre_options['convac_img5_title'] );
	set_theme_mod( 'brand5_img', $convac_lite_pre_options['convac_img5_icon'] );
	set_theme_mod( 'brand5_url', $convac_lite_pre_options['convac_img5_link'] );
	
	set_theme_mod( 'blogpage_heading', $convac_lite_pre_options['convac_blogpage_heading'] );
	if( $convac_lite_pre_options['convac_show_pagination'] == 'true' )
		set_theme_mod( 'blogpage_custom_pagination', 'on' );
	else
		set_theme_mod( 'blogpage_custom_pagination', 'off' );
	
	if( $convac_lite_pre_options['convac_hide_bread'] == 'true' )
		set_theme_mod( 'breadcrumb_sec', 'on' );
	else
		set_theme_mod( 'breadcrumb_sec', 'off' );

	set_theme_mod( 'breadcrumbtxt_color', $convac_lite_pre_options['convac_bread_title_color'] );
	set_theme_mod( 'breadcrumbbg_color', $convac_lite_pre_options['convac_bread_color'] );
	set_theme_mod( 'breadcrumbbg_image', $convac_lite_pre_options['convac_bread_image'] );
	
	set_theme_mod( 'copyright', $convac_lite_pre_options['convac_copyright'] );
	
	echo __('All the settings migrated successfully.', 'convac-lite');

	delete_option( 'convac_lite' );

	die();
}

add_action('admin_menu', 'convac_lite_migrate_menu');
function convac_lite_migrate_menu() {
	add_theme_page( __('Convac Migrate Options', 'convac-lite'), __('Convac Migrate Options', 'convac-lite'), 'administrator', 'sktmigrate', 'convac_lite_migrate_menu_options' );
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