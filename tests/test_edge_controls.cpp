#include "omnivoice_internal.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <vector>
using namespace omnivoice;
int main() {
    assert(normalize_terminal_punctuation_spacing("Hola!") == "Hola !");
    assert(normalize_terminal_punctuation_spacing("Hola! Mundo?") == "Hola ! Mundo ?");
    assert(normalize_terminal_punctuation_spacing("Hola !!!") == "Hola !!!");
    assert(normalize_terminal_punctuation_spacing("Jesteśmy gotowi do ofiary!") == "Jesteśmy gotowi do ofiary !");
    assert(normalize_terminal_punctuation_spacing("¿Listo?") == "¿Listo ?");
    assert(normalize_terminal_punctuation_spacing("你好?") == "你好?");
    assert(normalize_terminal_punctuation_spacing("こんにちは!") == "こんにちは!");
    assert(normalize_terminal_punctuation_spacing("안녕!") == "안녕!");
    assert(normalize_terminal_punctuation_spacing("Hola .") == "Hola .");
    assert(normalize_terminal_punctuation_spacing("Hola!Mundo") == "Hola!Mundo");
    std::vector<float> audio(2400,0.5f);
    auto legacy=fade_and_pad_audio(audio,24000,0.1f,0.1f);
    assert(legacy.size()==audio.size()+4800);
    assert(legacy.front()==0.0f && legacy.back()==0.0f);
    assert(legacy[2400] == 0.0f);
    auto safe=fade_and_pad_audio(audio,24000,0.0f,0.1f);
    assert(safe.size()==legacy.size());
    assert(safe[2400] == 0.5f && safe[2399] == 0.0f);
    auto raw=fade_and_pad_audio(audio,24000,0.0f,0.0f);
    assert(raw.size()==audio.size() && raw.front()==0.5f && raw.back()==0.5f);
    std::vector<float> tail(24000,0.0f);
    for(size_t i=2400;i<12000;i++) tail[i]=0.2f;
    for(size_t i=12000;i<23999;i++) tail[i]=0.0005f;
    const auto trim=remove_silence(tail,24000,0,100,100,false);
    const auto keep=remove_silence(tail,24000,0,100,100,true);
    assert(trim.size()<keep.size());
    assert(keep.size()==tail.size());
    assert(keep[23998]!=0.0f);
    std::cout<<"EDGE_CONTROLS_TEST_OK: punctuation, fade, pad and weak tail preservation\n";
}
