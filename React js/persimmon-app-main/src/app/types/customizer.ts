export interface Color {
    id: string
    value: string
  }
  
  export interface CustomizerState {
    darkMode: boolean
    primaryColor: string
    colors: Color[]
    fontFamily: string
    coverImage: boolean
    heading: string
    description: string
  }
  
  export interface PreviewProps {
    settings: CustomizerState
  }
  
  