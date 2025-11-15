const { SlashCommandBuilder } = require('discord.js');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('guess')
        .setDescription('Çizim oyununda kelime tahmini yapar.')
        .addStringOption(option =>
            option.setName('tahmin')
                .setDescription('Tahmininiz')
                .setRequired(true)),
    async execute(interaction) {
        await interaction.reply({
            content: '🤔 Çizim oyunu özelliği henüz geliştirilme aşamasındadır.',
            ephemeral: true
        });
    }
};
