package com.crosspostme;

import dagger.hilt.InstallIn;
import dagger.hilt.codegen.OriginatingElement;
import dagger.hilt.components.SingletonComponent;
import dagger.hilt.internal.GeneratedEntryPoint;

@OriginatingElement(
    topLevelClass = CrossPostMeApplication.class
)
@GeneratedEntryPoint
@InstallIn(SingletonComponent.class)
public interface CrossPostMeApplication_GeneratedInjector {
  void injectCrossPostMeApplication(CrossPostMeApplication crossPostMeApplication);
}
