import { useMemo } from 'react';

// Utility function to generate a seeded random number
const seededRandom = (seed: string, index: number): number => {
  const char = seed.charCodeAt(Math.min(index, seed.length - 1));
  return (char / 255);
};

// Available Tailwind gradient colors
const gradientColors = [
  'from-red-500',
  'from-orange-500',
  'from-amber-500',
  'from-yellow-500',
  'from-lime-500',
  'from-green-500',
  'from-emerald-500',
  'from-teal-500',
  'from-cyan-500',
  'from-sky-500',
  'from-blue-500',
  'from-indigo-500',
  'from-violet-500',
  'from-purple-500',
  'from-fuchsia-500',
  'from-pink-500',
  'from-rose-500',
];

const toColors = gradientColors.map(color => color.replace('from-', 'to-'));
const viaColors = gradientColors.map(color => color.replace('from-', 'via-'));

// Generate gradient direction classes
const directions = [
  'bg-gradient-to-r',
  'bg-gradient-to-br',
  'bg-gradient-to-b',
  'bg-gradient-to-bl',
  'bg-gradient-to-l',
  'bg-gradient-to-tl',
  'bg-gradient-to-t',
  'bg-gradient-to-tr',
];

// Function to select a random item from array using seed
const getRandomItem = (arr: string[], seed: string, index: number): string => {
  const randomIndex = Math.floor(seededRandom(seed, index) * arr.length);
  return arr[randomIndex];
};

// Main function to generate gradient classes
export const generateGradientClasses = (hash: string): string => {
  // Get seeded random direction
  const direction = getRandomItem(directions, hash, 0);
  
  // Get seeded random colors
  const fromColor = getRandomItem(gradientColors, hash, 1);
  const viaColor = getRandomItem(viaColors, hash, 2);
  const toColor = getRandomItem(toColors, hash, 3);
  
  // Opacity classes
  const fromOpacity = Math.floor(seededRandom(hash, 4) * 100);
  const viaOpacity = Math.floor(seededRandom(hash, 5) * 100);
  const toOpacity = Math.floor(seededRandom(hash, 6) * 100);
  
  // Combine classes
  const classes = `${direction} ${fromColor} ${viaColor} ${toColor} from-${fromOpacity} via-${viaOpacity} to-${toOpacity} bg-gradient-to-r`;
  console.log(classes)
  return classes;
};

// React component with Tailwind classes
export const GradientBackground: React.FC<{ 
  hash: string;
  className?: string;
}> = ({ hash, className = '' }) => {
  // Memoize the gradient classes
  const gradientClasses = useMemo(() => generateGradientClasses(hash), [hash]);
  
  return (
    <div className={`${gradientClasses} ${className}`} />
  );
};

// Example animation component with multiple gradients
export const AnimatedGradients: React.FC<{
  hash: string;
  className?: string;
}> = ({ hash, className = '' }) => {
  // Generate multiple gradient variations from the same hash
  const gradients = useMemo(() => (
    Array.from({ length: 3 }, (_, i) => 
      generateGradientClasses(`${hash}-${i}`)
    )
  ), [hash]);

  return (
    <div className="relative w-full h-full">
      {gradients.map((gradient, index) => (
        <div
          key={index}
          className={`
            absolute inset-0 transition-opacity duration-1000
            ${gradient} ${className}
            ${index === 0 ? 'animate-gradient-1' : ''}
            ${index === 1 ? 'animate-gradient-2' : ''}
            ${index === 2 ? 'animate-gradient-3' : ''}
          `}
        />
      ))}
    </div>
  );
};