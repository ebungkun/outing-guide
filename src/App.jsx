import React, { useState, useMemo, useEffect, useRef } from 'react';
// 1. src/data/preferences.json 파일을 생성하고, 그 안에 JSON 데이터를 붙여넣으세요.
// 2. 아래 import 구문이 해당 파일을 읽어옵니다.
import characterData from './data/preferences.json';

// --- Helper Function for Korean Search ---
const HANGUL_START = 44032; const HANGUL_END = 55203;
const CHO = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];
function isKorean(char) { const c = char.charCodeAt(0); return c >= HANGUL_START && c <= HANGUL_END; }
function getChosung(char) { if (!isKorean(char)) return char; const c = char.charCodeAt(0); return CHO[Math.floor((c - HANGUL_START) / 588)]; }
function matchesSearch(name, term) {
  term = term.toLowerCase().trim(); if (!term) return true;
  name = name.toLowerCase();
  if (name.includes(term)) return true;
  const chosungOnlyName = Array.from(name).map(getChosung).join('');
  return chosungOnlyName.includes(term);
}

// --- App Configuration ---
const typeColors = {
  '인간형': 'amber',
  '야수형': 'orange',
  '요정형': 'emerald',
  '불사형': 'indigo',
  '천악혼': 'fuchsia',
  '전체': 'neutral',
};

// --- Components ---

function FormattedCharacterName({ name, context, colorClass = 'text-sky-600' }) {
  const match = name.match(/^(.*?)\((.*?)\)$/);
  const mainName = match ? match[1] : name;
  const subName = match ? `(${match[2]})` : null;

  if (context === 'button') {
    return (
      <div className="flex flex-col items-center justify-center h-full leading-tight">
        <span>{mainName}</span>
        {subName && <span className="text-xs text-neutral-500 mt-1 font-light transition-colors">{subName}</span>}
      </div>
    );
  }

  if (context === 'cardTitle') {
    return (
      <h3 className={`text-2xl font-bold ${colorClass}`}>
        {mainName}
        {subName && <span className="text-lg font-light ml-2">{subName}</span>}
      </h3>
    );
  }

  return <span>{name}</span>;
}

function SearchBar({ searchTerm, setSearchTerm, onFocus }) {
  return (
    <div className="relative w-full">
      <svg className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-neutral-400" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      <input
        type="text"
        placeholder="정령 이름 검색 (초성 지원)"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onFocus={onFocus}
        className="w-full px-4 py-3 pl-10 bg-white border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 transition-shadow"
      />
    </div>
  );
}

function TypeFilter({ types, selectedType, setSelectedType }) {
  return (
    <div className="flex flex-wrap gap-2">
      {types.map(type => {
        const color = typeColors[type] || 'neutral';
        const isSelected = selectedType === type;

        const baseClasses = "px-4 py-2 text-sm rounded-full transition-all duration-200 border-2";
        const selectedClasses = `bg-white text-${color}-600 border-${color}-500 scale-105 shadow-md`;
        const unselectedClasses = `bg-white text-neutral-700 border-neutral-300 hover:text-${color}-600 hover:border-${color}-500`;

        return (
          <button key={type} onClick={() => setSelectedType(type)}
            className={`${baseClasses} ${isSelected ? selectedClasses : unselectedClasses}`}
          >
            {type}
          </button>
        );
      })}
    </div>
  );
}

function PreferenceList({ title, preferences, choicesMap }) {
  if (!preferences || !preferences.liked || !preferences.disliked) return null;

  const PreferenceItems = ({ ids, isLiked }) => {
    const likedTextColor = 'text-sky-700';
    const dislikedTextColor = 'text-red-700';
    const cardBgColor = isLiked ? 'bg-sky-100' : 'bg-red-100';

    return (
      <div className="flex flex-wrap gap-2">
        {ids.map(id => {
          const choiceData = choicesMap[id];
          if (!choiceData) return null;

          const { choice, location } = choiceData;
          const isCommon = location === "어디서나";

          if (isCommon) {
            return (
              <div key={id} className={`p-3 ${cardBgColor} rounded-lg`}>
                <p className={`text-md ${isLiked ? likedTextColor : dislikedTextColor}`}>{choice}</p>
              </div>
            );
          }

          return (
            <div key={id} className={`p-3 ${cardBgColor} rounded-lg`}>
              <p className="text-sm text-neutral-500">{location}</p>
              <p className={`text-md ${isLiked ? likedTextColor : dislikedTextColor} mt-1`}>{choice}</p>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="bg-neutral-100/70 p-4 rounded-lg border border-neutral-200/80">
      <h4 className="font-bold text-md text-neutral-600 mb-3 pl-2">{title}</h4>
      <div className="space-y-4">
        <div className="flex items-center">
          <span className="text-red-500 text-2xl mr-4">❤️</span>
          <PreferenceItems ids={preferences.liked} isLiked={true} />
        </div>
        <div className="flex items-center">
          <span className="text-yellow-500 text-2xl mr-4">💛</span>
          <PreferenceItems ids={preferences.disliked} isLiked={false} />
        </div>
      </div>
    </div>
  );
}

// [MODIFIED] CharacterCard component to display the source URL.
// [수정됨] 출처 URL을 표시하도록 CharacterCard 컴포넌트를 수정했습니다.
function CharacterCard({ character, choicesMap, onClear }) {
  const { character_name, preferences, type, url } = character; // Destructure url from character prop
  const color = typeColors[type] || 'sky';
  const borderColorClass = `border-${color}-500`;
  const textColorClass = `text-${color}-700`;

  return (
    <div className={`bg-white/80 backdrop-blur-sm rounded-lg shadow-lg p-6 border-2 ${borderColorClass} animate-fade-in`}>
       <div className="flex justify-between items-start">
        {/* Left side: Title and Source Link */}
        <div>
          <FormattedCharacterName name={character_name} context="cardTitle" colorClass={textColorClass} />
          {/* Source Link: Render only if URL exists */}
          {url && (
            <div className="mt-2">
              <a 
                href={url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="inline-flex items-center text-sm text-neutral-500 hover:text-sky-600 transition-colors group"
              >
                <span className="mr-1.5">출처:</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-link group-hover:animate-pulse"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.72"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.72-1.72"/></svg>
              </a>
            </div>
          )}
        </div>
        
        {/* Right side: Close Button */}
        <button onClick={onClear} className="text-neutral-500 hover:text-neutral-800 transition-colors flex-shrink-0 ml-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
       </div>
      <div className="mt-6 flex flex-col gap-4">
        <PreferenceList title="커먼" preferences={preferences.common} choicesMap={choicesMap} />
        <PreferenceList title="레어 (낮)" preferences={preferences.rare_day} choicesMap={choicesMap} />
        <PreferenceList title="레어 (밤)" preferences={preferences.rare_night} choicesMap={choicesMap} />
      </div>
    </div>
  );
}

function CharacterList({ characters, onSelectCharacter }) {
    return (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 mt-6 animate-fade-in">
            {characters.map(char => {
                const color = typeColors[char.type] || 'sky';
                const hoverClasses = `hover:border-${color}-500 hover:shadow-md hover:-translate-y-0.5`;

                return (
                    <button 
                        key={char.character_name}
                        onClick={() => onSelectCharacter(char)}
                        className={`text-center p-2 h-16 bg-white text-neutral-800 rounded-lg border-2 border-transparent ${hoverClasses} transition-all duration-200 focus:outline-none group`}
                    >
                        <FormattedCharacterName name={char.character_name} context="button" />
                    </button>
                )
            })}
        </div>
    );
}

// --- Main App Component ---

export default function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('전체');
  const [selectedCharacter, setSelectedCharacter] = useState(null);
  const [isInteracting, setIsInteracting] = useState(false);
  
  const cardRef = useRef(null);
  const headerRef = useRef(null);
  const disappearingHeaderHeight = useRef(0);

  const { mapping_tables, character_preferences } = characterData;
  
  const orderedTypes = ['인간형', '야수형', '요정형', '불사형', '천악혼'];
  const characterTypes = ['전체', ...orderedTypes];
  
  const allCharacters = useMemo(() => {
    return Object.entries(character_preferences)
        .flatMap(([type, chars]) => chars.map(char => ({ ...char, type })))
        .sort((a, b) => a.character_name.localeCompare(b.character_name, 'ko'));
  }, [character_preferences]);

  const filteredCharacters = useMemo(() => {
    return allCharacters
      .filter(char => selectedType === '전체' || char.type === selectedType)
      .filter(char => matchesSearch(char.character_name, searchTerm));
  }, [searchTerm, selectedType, allCharacters]);

  const startInteraction = () => {
    if (!isInteracting && headerRef.current) {
      disappearingHeaderHeight.current = headerRef.current.offsetHeight;
    } else {
      disappearingHeaderHeight.current = 0;
    }
    setIsInteracting(true);
  };

  useEffect(() => {
    setSelectedCharacter(null);
    if(searchTerm || selectedType !== '전체') {
      startInteraction();
    }
  }, [searchTerm, selectedType]);
  
  useEffect(() => { 
      if (filteredCharacters.length === 1) { 
          startInteraction();
          setSelectedCharacter(filteredCharacters[0]);
      } 
  }, [filteredCharacters]);

  useEffect(() => {
    if (selectedCharacter && cardRef.current) {
      if (cardRef.current) {
        let topMargin = 16; 

        if (window.innerWidth >= 768) {
          const stickyHeaderElement = document.querySelector('.md\\:sticky');
          if (stickyHeaderElement) {
            topMargin = stickyHeaderElement.offsetHeight + 16;
          }
        }

        const elementPosition = cardRef.current.getBoundingClientRect().top;
        let offsetPosition = elementPosition + window.scrollY - topMargin;

        if (disappearingHeaderHeight.current > 0) {
          offsetPosition -= disappearingHeaderHeight.current;
        }

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    }
  }, [selectedCharacter]);

  const handleSelectCharacter = (character) => { 
      startInteraction();
      setSelectedCharacter(character);
  };

  const handleClearSelection = () => { 
      setSelectedCharacter(null); 
      setSearchTerm('');
      setSelectedType('전체');
      setIsInteracting(false);
  }

  return (
    <div className="bg-neutral-50 min-h-screen text-neutral-800 font-sans">
      <div className="container mx-auto max-w-3xl p-4">
        <header ref={headerRef} className={`text-center ${isInteracting ? 'h-0 opacity-0 my-0 overflow-hidden' : 'my-4'}`}>
            <h1 className="text-3xl font-bold text-sky-600">에버소울 나들이 가이드</h1>
        </header>
        <main>
          <div className={`space-y-4 p-4 bg-white/60 backdrop-blur-lg md:sticky top-4 z-10 rounded-xl shadow-sm border border-neutral-200`}>
            <SearchBar 
                searchTerm={searchTerm} 
                setSearchTerm={setSearchTerm}
                onFocus={startInteraction}
            />
            <TypeFilter types={characterTypes} selectedType={selectedType} setSelectedType={setSelectedType} />
          </div>
          <div className="mt-8">
            {selectedCharacter ? (
              <div ref={cardRef}>
                <CharacterCard 
                  character={selectedCharacter} 
                  choicesMap={mapping_tables.choices}
                  onClear={handleClearSelection}
                />
              </div>
            ) : (
                <>
                    {filteredCharacters.length > 0 ? (
                         <CharacterList 
                            characters={filteredCharacters}
                            onSelectCharacter={handleSelectCharacter}
                         />
                    ) : (
                        <p className="text-center text-neutral-500 mt-8">검색 결과가 없습니다.</p>
                    )}
                </>
            )}
          </div>
        </main>
        <footer className="text-center text-xs text-neutral-400 mt-12 pb-4">
            <p>공략 제공: 에버소울 챈/갤 유저들</p>
            <p className="mt-1">앱 제작: 에붕소울 (아카라이브 에버소울 채널)</p>
        </footer>
      </div>
    </div>
  );
}
