import { ChangeDetectionStrategy, Component, inject, PLATFORM_ID } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet, Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-public-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './public-layout.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PublicLayoutComponent {
  private router = inject(Router);
  private platformId = inject(PLATFORM_ID);

  scrollTo(event: MouseEvent, id: string) {
    if (!isPlatformBrowser(this.platformId)) return;
    event.preventDefault();
    
    if (window.location.pathname.endsWith('/home') || window.location.pathname === '/') {
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      this.router.navigate(['/home']).then(() => {
        setTimeout(() => {
          const el = document.getElementById(id);
          if (el) {
            el.scrollIntoView({ behavior: 'smooth' });
          }
        }, 150);
      });
    }
  }
}

