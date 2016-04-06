<?php
/**
 * The base configurations of the WordPress.
 *
 * This file has the following configurations: MySQL settings, Table Prefix,
 * Secret Keys, WordPress Language, and ABSPATH. You can find more information
 * by visiting {@link http://codex.wordpress.org/Editing_wp-config.php Editing
 * wp-config.php} Codex page. You can get the MySQL settings from your web host.
 *
 * This file is used by the wp-config.php creation script during the
 * installation. You don't have to use the web site, you can just copy this file
 * to "wp-config.php" and fill in the values.
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'WPCACHEHOME', '/home3/whweaver/public_html/willweaver.net/wp-content/plugins/wp-super-cache/' ); //Added by WP-Cache Manager
define('WP_CACHE', true); //Added by WP-Cache Manager
define('DB_NAME', 'whweaver_wrdp2');

/** MySQL database username */
define('DB_USER', 'whweaver_wrdp2');

/** MySQL database password */
define('DB_PASSWORD', '2DnCNkfOuBtxO5N');

/** MySQL hostname */
define('DB_HOST', 'localhost');

/** Database Charset to use in creating database tables. */
define('DB_CHARSET', 'utf8');

/** The Database Collate type. Don't change this if in doubt. */
define('DB_COLLATE', '');

/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define('AUTH_KEY',         'SI$^_>0oa:JF/G18*0M3!o~h?3y-!G4G<kEeoK\`u$MNl>GxVQhqhX0!sIu)b*');
define('SECURE_AUTH_KEY',  '');
define('LOGGED_IN_KEY',    'livk#^tnYT:!QvILd7t6Z/iSc^~5hZ_~-E49EfEO9RzdNQcpPeEye)YH@hbE>s^co00U6M>K@Gi)H6cHP7k\`\`z3');
define('NONCE_KEY',        '#/$bcm8mH=^vjXgyjwYx4YRc|Vm7\`t8sTtlyu2!)#?K^Pc1aAIx3#\`u\`_;m_\`CS1');
define('AUTH_SALT',        'zuAa:1B0AwjL4VAK\`-\`vd7Pe_3PBHKMyf)3XQ9RTcJ/CtS(:n4_Ju(4Ur<@VPkX)cl>CUu');
define('SECURE_AUTH_SALT', 'b4W!u2Xe*S$^|UeRj4T/E:ofK*tErST;gpu<!#16XVpG>afvACB(|!fyCgr1O@Wyvljn7Yx');
define('LOGGED_IN_SALT',   'S=0H<6Dr3EZpx<8Ynpm*M1TG=~t^soJG:mo/gMl(X;FFcO/Fp523WGF*6anVD!iI?:CJE@_>k');
define('NONCE_SALT',       'Ir7eP~P_D!\`MdHVqo>daE\`jc:oFUjYmRqng@6YQ/HAI>!?GIK;2K\`eU|ag3tq5K_/UcYeg\`');

/**#@-*/
define('AUTOSAVE_INTERVAL', 600 );
define('WP_POST_REVISIONS', 1);
define( 'WP_CRON_LOCK_TIMEOUT', 120 );
define( 'WP_AUTO_UPDATE_CORE', true );
/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each a unique
 * prefix. Only numbers, letters, and underscores please!
 */
$table_prefix  = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 */
define('WP_DEBUG', false);

/* That's all, stop editing! Happy blogging. */

/** Absolute path to the WordPress directory. */
if ( !defined('ABSPATH') )
	define('ABSPATH', dirname(__FILE__) . '/');

/** Sets up WordPress vars and included files. */
require_once(ABSPATH . 'wp-settings.php');
add_filter( 'auto_update_plugin', '__return_true' );
add_filter( 'auto_update_theme', '__return_true' );
