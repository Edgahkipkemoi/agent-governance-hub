-- Enable Row Level Security and create policies for the logs table

-- Enable RLS on the logs table
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

-- Create policy to allow anyone to read logs (for the dashboard)
CREATE POLICY "Allow public read access to logs"
ON logs
FOR SELECT
USING (true);

-- Create policy to allow service role to insert logs
CREATE POLICY "Allow service role to insert logs"
ON logs
FOR INSERT
WITH CHECK (true);

-- Create policy to allow service role to update logs
CREATE POLICY "Allow service role to update logs"
ON logs
FOR UPDATE
USING (true);

-- Create policy to allow service role to delete logs
CREATE POLICY "Allow service role to delete logs"
ON logs
FOR DELETE
USING (true);
