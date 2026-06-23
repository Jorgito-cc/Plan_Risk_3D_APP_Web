import { Injectable, signal, PLATFORM_ID, inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

// ─── Diccionarios de traducción inline ────────────────────────────
const ES: Record<string, string> = {
  // ── Header / Nav ──
  'nav.home': 'Inicio',
  'nav.features': 'Funcionalidades',
  'nav.viewer': 'Visor 3D',
  'nav.pricing': 'Suscripciones',
  'nav.faq': 'FAQ',
  'nav.login': 'Iniciar Sesión',
  'nav.subtitle': 'Ingeniería & IA',

  // ── Footer ──
  'footer.description': 'Plataforma avanzada de modelado estructural y predicción de fallas asistida por Inteligencia Artificial y asegurada con tecnología Blockchain.',
  'footer.quickLinks': 'Enlaces Rápidos',
  'footer.terms': 'Términos',
  'footer.privacy': 'Privacidad',
  'footer.techEcosystem': 'Ecosistema Técnico',
  'footer.techDescription': 'Diseñado con estándares premium para la industria de la ingeniería civil y estructural.',

  // ── Login ──
  'login.welcome': 'Bienvenido a',
  'login.email': 'Correo electrónico',
  'login.emailPlaceholder': 'tu@correo.com',
  'login.emailError': 'Por favor ingrese un correo electrónico válido',
  'login.password': 'Contraseña',
  'login.submit': 'INICIAR SESIÓN',
  'login.forgot': '¿Olvidaste tu contraseña?',
  'login.register': 'Registrarse',

  // ── Register ──
  'register.title': 'Crea tu cuenta en',
  'register.name': 'Nombre',
  'register.namePlaceholder': 'Juan',
  'register.surname': 'Apellido',
  'register.surnamePlaceholder': 'Pérez',
  'register.email': 'Correo electrónico',
  'register.emailPlaceholder': 'tu@correo.com',
  'register.password': 'Contraseña',
  'register.passwordPlaceholder': '••••••••',
  'register.phone': 'Teléfono / Celular',
  'register.phonePlaceholder': '76543210',
  'register.profession': 'Profesión',
  'register.profStudent': 'Estudiante',
  'register.profProfessional': 'Profesional',
  'register.profOther': 'Otro',
  'register.birthDate': 'Fecha de Nacimiento',
  'register.acceptPolicies': 'Acepto los',
  'register.termsLink': 'Términos y Condiciones',
  'register.andThe': 'y la',
  'register.privacyLink': 'Política de Privacidad',
  'register.ofPR3D': 'de Plan Risk 3D.',
  'register.submit': 'REGISTRARSE',
  'register.hasAccount': '¿Ya tienes cuenta? Ingresa',
  'register.backHome': 'Volver a Inicio',

  // ── Sidebar / Private layout ──
  'sidebar.profile': 'Perfil',
  'sidebar.projects': 'Proyectos',
  'sidebar.editor': 'Editor 3D',
  'sidebar.logout': 'Salir',

  // ── Dashboard ──
  'dashboard.title': 'Mis Proyectos',
  'dashboard.new': 'Nuevo Proyecto',
  'dashboard.empty': 'No tienes proyectos aún',
  'dashboard.upload': 'Subir Plano',
  'dashboard.delete': 'Eliminar',
  'dashboard.view': 'Ver Modelo',
  'dashboard.download': 'Descargar GLB',
  'dashboard.share': 'Compartir',

  // ── Perfil ──
  'profile.title': 'Mi Perfil',
  'profile.name': 'Nombre',
  'profile.email': 'Correo',
  'profile.plan': 'Plan Actual',
  'profile.save': 'Guardar Cambios',
  'profile.photo': 'Foto de Perfil',
  'profile.changePhoto': 'Cambiar Foto',

  // ── Home page ──
  'home.heroTitle': 'Transforma Planos en Modelos 3D',
  'home.heroSubtitle': 'Potenciado por IA',
  'home.heroCTA': 'Comenzar Ahora',
  'home.heroSecondaryCTA': 'Ver Demo',

  // ── Genéricos ──
  'generic.loading': 'Cargando...',
  'generic.error': 'Ha ocurrido un error',
  'generic.success': 'Operación exitosa',
  'generic.cancel': 'Cancelar',
  'generic.confirm': 'Confirmar',
  'generic.save': 'Guardar',
  'generic.delete': 'Eliminar',
  'generic.edit': 'Editar',
  'generic.close': 'Cerrar',
  'generic.search': 'Buscar',

  // ── Lang toggle ──
  'lang.switch': 'EN',
  'lang.tooltip': 'Switch to English',
};

const EN: Record<string, string> = {
  // ── Header / Nav ──
  'nav.home': 'Home',
  'nav.features': 'Features',
  'nav.viewer': '3D Viewer',
  'nav.pricing': 'Pricing',
  'nav.faq': 'FAQ',
  'nav.login': 'Sign In',
  'nav.subtitle': 'Engineering & AI',

  // ── Footer ──
  'footer.description': 'Advanced structural modeling platform with AI-powered failure prediction and Blockchain-secured technology.',
  'footer.quickLinks': 'Quick Links',
  'footer.terms': 'Terms',
  'footer.privacy': 'Privacy',
  'footer.techEcosystem': 'Tech Ecosystem',
  'footer.techDescription': 'Designed with premium standards for the civil and structural engineering industry.',

  // ── Login ──
  'login.welcome': 'Welcome to',
  'login.email': 'Email address',
  'login.emailPlaceholder': 'you@email.com',
  'login.emailError': 'Please enter a valid email address',
  'login.password': 'Password',
  'login.submit': 'SIGN IN',
  'login.forgot': 'Forgot your password?',
  'login.register': 'Sign Up',

  // ── Register ──
  'register.title': 'Create your account on',
  'register.name': 'First Name',
  'register.namePlaceholder': 'John',
  'register.surname': 'Last Name',
  'register.surnamePlaceholder': 'Doe',
  'register.email': 'Email address',
  'register.emailPlaceholder': 'you@email.com',
  'register.password': 'Password',
  'register.passwordPlaceholder': '••••••••',
  'register.phone': 'Phone / Mobile',
  'register.phonePlaceholder': '76543210',
  'register.profession': 'Profession',
  'register.profStudent': 'Student',
  'register.profProfessional': 'Professional',
  'register.profOther': 'Other',
  'register.birthDate': 'Date of Birth',
  'register.acceptPolicies': 'I accept the',
  'register.termsLink': 'Terms and Conditions',
  'register.andThe': 'and the',
  'register.privacyLink': 'Privacy Policy',
  'register.ofPR3D': 'of Plan Risk 3D.',
  'register.submit': 'SIGN UP',
  'register.hasAccount': 'Already have an account? Sign In',
  'register.backHome': 'Back to Home',

  // ── Sidebar / Private layout ──
  'sidebar.profile': 'Profile',
  'sidebar.projects': 'Projects',
  'sidebar.editor': '3D Editor',
  'sidebar.logout': 'Log Out',

  // ── Dashboard ──
  'dashboard.title': 'My Projects',
  'dashboard.new': 'New Project',
  'dashboard.empty': 'You have no projects yet',
  'dashboard.upload': 'Upload Plan',
  'dashboard.delete': 'Delete',
  'dashboard.view': 'View Model',
  'dashboard.download': 'Download GLB',
  'dashboard.share': 'Share',

  // ── Perfil ──
  'profile.title': 'My Profile',
  'profile.name': 'Name',
  'profile.email': 'Email',
  'profile.plan': 'Current Plan',
  'profile.save': 'Save Changes',
  'profile.photo': 'Profile Photo',
  'profile.changePhoto': 'Change Photo',

  // ── Home page ──
  'home.heroTitle': 'Transform Blueprints into 3D Models',
  'home.heroSubtitle': 'Powered by AI',
  'home.heroCTA': 'Get Started',
  'home.heroSecondaryCTA': 'Watch Demo',

  // ── Genéricos ──
  'generic.loading': 'Loading...',
  'generic.error': 'An error occurred',
  'generic.success': 'Operation successful',
  'generic.cancel': 'Cancel',
  'generic.confirm': 'Confirm',
  'generic.save': 'Save',
  'generic.delete': 'Delete',
  'generic.edit': 'Edit',
  'generic.close': 'Close',
  'generic.search': 'Search',

  // ── Lang toggle ──
  'lang.switch': 'ES',
  'lang.tooltip': 'Cambiar a Español',
};

@Injectable({ providedIn: 'root' })
export class TranslateService {
  private platformId = inject(PLATFORM_ID);

  /** Signal reactivo con el idioma actual */
  currentLang = signal<'es' | 'en'>(this.getStoredLang());

  private dictionaries: Record<string, Record<string, string>> = { es: ES, en: EN };

  /** Obtiene la traducción para una clave */
  t(key: string): string {
    const dict = this.dictionaries[this.currentLang()];
    return dict?.[key] ?? key;
  }

  /** Alterna entre español e inglés */
  toggle(): void {
    const newLang = this.currentLang() === 'es' ? 'en' : 'es';
    this.currentLang.set(newLang);
    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('pr3d_lang', newLang);
    }
  }

  private getStoredLang(): 'es' | 'en' {
    if (isPlatformBrowser(this.platformId)) {
      const stored = localStorage.getItem('pr3d_lang');
      if (stored === 'en' || stored === 'es') return stored;
    }
    return 'es';
  }
}
