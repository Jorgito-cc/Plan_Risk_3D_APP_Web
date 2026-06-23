import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface Message {
  sender: 'bot' | 'user';
  text: string;
}

@Component({
  selector: 'app-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css']
})
export class ChatbotComponent implements AfterViewChecked {
  isOpen = false;
  isLoading = false;
  inputValue = '';
  
  messages: Message[] = [
    {
      sender: 'bot',
      text: '¡Hola! Soy el asistente de Plan Risk 3D. ¿En qué te puedo ayudar hoy?'
    }
  ];

  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;

  constructor(private http: HttpClient) {}

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  toggleChat() {
    this.isOpen = !this.isOpen;
    if (this.isOpen) {
      setTimeout(() => this.scrollToBottom(), 100);
    }
  }

  scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
      }
    } catch (err) {}
  }

  async handleSend() {
    if (!this.inputValue.trim()) return;

    const userText = this.inputValue;
    this.messages.push({ sender: 'user', text: userText });
    this.inputValue = '';
    this.isLoading = true;

    // We use the backend URL configured for Django
    const apiUrl = 'http://localhost:8000/api/suggestion_risk/chat/';

    this.http.post<any>(apiUrl, { query: userText }).subscribe({
      next: (data) => {
        if (data.respuesta) {
          this.messages.push({ sender: 'bot', text: data.respuesta });
        } else {
          this.messages.push({ sender: 'bot', text: 'Respuesta inesperada del servidor.' });
        }
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error enviando mensaje:', err);
        const errorMsg = err.error?.error || err.message || 'Error desconocido';
        this.messages.push({ sender: 'bot', text: `Error del servidor: ${errorMsg}` });
        this.isLoading = false;
      }
    });
  }

  handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      this.handleSend();
    }
  }
}
