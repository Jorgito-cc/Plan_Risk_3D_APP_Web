import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ChatbotComponent } from './layout/components/chatbot/chatbot.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ChatbotComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('front_plan_risk_3d');
}
