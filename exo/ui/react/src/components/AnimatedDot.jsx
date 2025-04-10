import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';
import * as THREE from 'three';

const DotContainer = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  z-index: 10;
  pointer-events: none;
`;

const AnimatedDot = ({ state = 'idle' }) => {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const dotRef = useRef(null);
  const frameIdRef = useRef(null);
  
  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current) return;
    
    // Create scene
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    
    // Create camera
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    camera.position.z = 5;
    cameraRef.current = camera;
    
    // Create renderer
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(200, 200);
    renderer.setClearColor(0x000000, 0);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;
    
    // Create dot geometry
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    const material = new THREE.MeshBasicMaterial({ color: 0x6200ee });
    const dot = new THREE.Mesh(geometry, material);
    scene.add(dot);
    dotRef.current = dot;
    
    // Start animation loop
    const animate = () => {
      frameIdRef.current = requestAnimationFrame(animate);
      
      // Update dot based on state
      updateDot(state);
      
      // Render scene
      renderer.render(scene, camera);
    };
    
    animate();
    
    // Cleanup
    return () => {
      cancelAnimationFrame(frameIdRef.current);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
    };
  }, []);
  
  // Update dot animation based on state
  const updateDot = (state) => {
    if (!dotRef.current) return;
    
    const dot = dotRef.current;
    
    switch (state) {
      case 'idle':
        // Gentle pulsing animation
        dot.scale.x = 1 + Math.sin(Date.now() * 0.001) * 0.1;
        dot.scale.y = 1 + Math.sin(Date.now() * 0.001) * 0.1;
        dot.scale.z = 1 + Math.sin(Date.now() * 0.001) * 0.1;
        dot.material.color.set(0x6200ee);
        break;
        
      case 'listening':
        // Responsive ripple animation
        dot.scale.x = 1 + Math.sin(Date.now() * 0.003) * 0.2;
        dot.scale.y = 1 + Math.sin(Date.now() * 0.003) * 0.2;
        dot.scale.z = 1 + Math.sin(Date.now() * 0.003) * 0.2;
        dot.material.color.set(0x03dac6);
        break;
        
      case 'processing':
        // Fluid motion indicating computation
        dot.rotation.x += 0.01;
        dot.rotation.y += 0.01;
        dot.scale.x = 1 + Math.sin(Date.now() * 0.002) * 0.15;
        dot.scale.y = 1 + Math.sin(Date.now() * 0.002) * 0.15;
        dot.scale.z = 1 + Math.sin(Date.now() * 0.002) * 0.15;
        dot.material.color.set(0xbb86fc);
        break;
        
      case 'speaking':
        // Movements synchronized with speech
        dot.scale.x = 1 + Math.sin(Date.now() * 0.01) * 0.15;
        dot.scale.y = 1 + Math.sin(Date.now() * 0.01) * 0.15;
        dot.scale.z = 1 + Math.sin(Date.now() * 0.01) * 0.15;
        dot.material.color.set(0x6200ee);
        break;
        
      case 'error':
        // Distinct animation for errors
        dot.scale.x = 1 + Math.sin(Date.now() * 0.005) * 0.3;
        dot.scale.y = 1 + Math.sin(Date.now() * 0.005) * 0.3;
        dot.scale.z = 1 + Math.sin(Date.now() * 0.005) * 0.3;
        dot.material.color.set(0xcf6679);
        break;
        
      default:
        // Default to idle
        dot.scale.x = 1;
        dot.scale.y = 1;
        dot.scale.z = 1;
        dot.material.color.set(0x6200ee);
    }
  };
  
  // Update animation when state changes
  useEffect(() => {
    updateDot(state);
  }, [state]);
  
  return <DotContainer ref={containerRef} />;
};

export default AnimatedDot;
