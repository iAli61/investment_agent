import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Box, Link, Typography } from '@mui/material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';

/**
 * Component for rendering markdown content with proper formatting
 * @param {Object} props - Component props
 * @param {string} props.content - Markdown content to render
 */
const MarkdownView = ({ content }) => {
  return (
    <Box sx={{ 
      '& p': { mt: 1, mb: 1 },
      '& h1, & h2, & h3, & h4, & h5, & h6': { mt: 2, mb: 1 },
      '& ul, & ol': { pl: 2 }
    }}>
      <ReactMarkdown
        components={{
          // Override default renderers
          h1: ({ node, ...props }) => <Typography variant="h4" component="h1" fontWeight="bold" {...props} />,
          h2: ({ node, ...props }) => <Typography variant="h5" component="h2" fontWeight="bold" {...props} />,
          h3: ({ node, ...props }) => <Typography variant="h6" component="h3" fontWeight="bold" {...props} />,
          h4: ({ node, ...props }) => <Typography variant="subtitle1" component="h4" fontWeight="bold" {...props} />,
          h5: ({ node, ...props }) => <Typography variant="subtitle2" component="h5" fontWeight="bold" {...props} />,
          h6: ({ node, ...props }) => <Typography variant="subtitle2" component="h6" fontWeight="bold" {...props} />,
          p: ({ node, ...props }) => <Typography variant="body1" component="p" {...props} />,
          a: ({ node, ...props }) => <Link color="primary" target="_blank" rel="noopener" {...props} />,
          li: ({ node, ...props }) => <Typography component="li" variant="body1" {...props} />,
          code: ({ node, inline, className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={materialDark}
                language={match[1]}
                PreTag="div"
                {...props}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <Box 
                component="code" 
                sx={{ 
                  backgroundColor: 'grey.100', 
                  borderRadius: 1, 
                  px: 0.5, 
                  py: 0.25, 
                  fontFamily: 'monospace'
                }}
                {...props}
              >
                {children}
              </Box>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </Box>
  );
};

export default MarkdownView;