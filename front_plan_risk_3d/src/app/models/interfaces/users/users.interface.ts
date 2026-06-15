export interface UserInterface {
  id: number,
  nombre: string,
  apellido?: string,
  email: string,
  rol?: string,
  profesion?: string,
  fecha_nacimiento?: string,
  fecha_expiracion_plan?: string,
  fecha_registro?: string,
  telefono: string,
  url:string,
  acepta_politicas?: boolean,
  fecha_aceptacion?: string
}
export interface UserRegister {
  nombre: string,
  apellido?: string,
  email: string,
  password?: string,
  rol: string,
  profesion?: string,
  fecha_nacimiento?: string,
  fecha_expiracion_plan?: string,
  fecha_registro?: string,
  telefono: string,
  url:string,
  acepta_politicas?: boolean,
  fecha_aceptacion?: string
}

export interface UserLogin {
  email: string,
  password: string
}
export interface TopLevel {
  access: string;
  refresh: string;
  usuario: Usuario;
}

export interface Usuario {
  id: number;
  nombre: string;
  apellido?: string;
  email: string;
  password: string;
  rol: string;
  profesion?: string;
  fecha_nacimiento?: string;
  fecha_expiracion_plan?: string;
  fecha_registro?: string;
  telefono: string;
  url:string;
  acepta_politicas?: boolean;
  fecha_aceptacion?: string;
}



