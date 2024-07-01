import Link from 'next/link';
import { Button, Box } from '@mui/material';

export default function Home() {
  return (
    <div style={{ background: '#f0f0f0', minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <Box
        sx={{
          background: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.4)',
          maxWidth: '800px',
          width: '100%',
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: '20px',
          border: '1px solid black',   
        }}
      >
        <h1
          style={{
            fontSize: '32px',
            fontWeight: 'bold',
            color: '#000f',
            marginBottom: '20px',
            textAlign: 'center',
            width: '100%',
          }}
        >
          Welcome to Drishti Experiments
        </h1>
        <Link href="/dataextraction" passHref>
          <Button
            variant="contained"
            sx={{
              minWidth: '200px',
              flex: '1 0 200px',
              border: '1px solid black',  
              background: 'transparent',   
              color: 'black',
              '&:hover': {
                background: 'transparent',
                border: '1px solid black',
              },
            }}
          >
            Data Extraction
          </Button>
        </Link>
        <Link href="/datavalidation" passHref>
          <Button
            variant="contained"
            sx={{
              minWidth: '200px',
              flex: '1 0 200px',
              border: '1px solid black',
              background: 'transparent',
              color: 'black',
              '&:hover': {
                background: 'transparent',
                border: '1px solid black',
              },
            }}
          >
            Data Validation
          </Button>
        </Link>
        <Link href="/transcription" passHref>
          <Button
            variant="contained"
            sx={{
              minWidth: '200px',
              flex: '1 0 200px',
              border: '1px solid black',
              background: 'transparent',
              color: 'black',
              '&:hover': {
                background: 'transparent',
                border: '1px solid black',
              },
            }}
          >
            Transcription
          </Button>
        </Link>
      </Box>
    </div>
  );
}
