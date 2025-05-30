import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params; // Await params to resolve the dynamic route parameter
    console.log(`Fetching card with ID: ${id}`);
    console.log(`API URL: ${process.env.NEXT_PUBLIC_API_URL}`);
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/cards/${id}`, {
      credentials: 'include',
    });

    console.log(`Response status: ${response.status}`);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Error response: ${errorText}`);
      throw new Error(`Failed to fetch card: ${response.status} ${errorText}`);
    }

    const data = await response.json();
    console.log(`Successfully fetched card data: ${JSON.stringify(data)}`);
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in API route:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch card' },
      { status: 500 }
    );
  }
}